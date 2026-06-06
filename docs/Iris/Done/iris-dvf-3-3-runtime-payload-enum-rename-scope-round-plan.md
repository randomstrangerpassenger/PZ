# Iris DVF 3-3 Runtime Payload Enum Rename Scope Round Plan

> 상태: Draft v0.2-plan  
> 기준일: 2026-05-19  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Runtime Payload Enum Rename Scope Round - Synthesized ROADMAP` (2026-05-19 user-provided synthesis)  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`.  
> 실행 상태: planning authority only. 이 문서는 DVF 3-3 `runtime_state` operational payload enum rename scope를 확정하기 위한 실행 계획이며, 작성 시점에는 writer code, validator code, runtime Lua, rendered output, generated runtime artifact, quality_state, publish_state, deployed state, top-doc closeout state를 변경하지 않는다.

---

## 0. Round Opening Disclosure

Execution scale:

```text
governance
```

Mutable surfaces:

* Current operational writer enum emit paths, only after Phase 1 inventory classifies the exact surface as `canonical_rename`.
* Validator / intermediate consumer enum acceptance paths.
* Current test/golden fixtures, only when Phase 1 classifies them as operational current expected-output baselines.
* Branch B only: runtime-facing serialized enum token surfaces proven in scope by Phase 1.
* Phase 8 only: `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md` addenda.

Immutable surfaces:

* Historical sealed decision bodies.
* Rendered text.
* `quality_state` and `publish_state`.
* Row identity and row count.
* Compose authority.
* Chunk topology and deployable authority ownership.
* Browser/Wiki visibility policy.
* Pulse Core / Echo / Fuse / Nerve / Frame / Canvas surfaces.

Authority source and ownership:

```text
docs/Philosophy.md
  > docs/DECISIONS.md
  > docs/ARCHITECTURE.md
  > docs/ROADMAP.md
  > approved roadmap / approved plan
```

* Decision stage remains the only writer for `runtime_state`.
* Validator remains checker/gate only.
* Runtime consumers do not decide or rewrite state.

Mutation responsibility:

* Source writer changes must be generator/source edits.
* Generated artifact changes must be produced by the approved writer path identified by Phase 1.
* Generated authoritative artifacts must not be hand-edited.
* If an approved writer path for a generated authority artifact cannot be identified, that artifact cannot be mutated in this round and the affected surface must move to Branch C or a named follow-up round.

Failure semantics:

```text
failed inventory classification -> blocked_unclassified_authority_surface
unexplained hash delta -> blocked_unexplained_hash_delta
historical body mutation -> blocked_historical_body_rewrite_violation
dual-zero failure -> blocked_dual_zero_gate_failure
missing dynamic reach method -> blocked_dynamic_reach_method_missing
```

Validation ceiling:

* Static/build validation and targeted smoke only.
* No deployed closeout.
* No in-game QA pass.
* No release readiness.

Equivalence proof method:

* Row count and adopted/unadopted split parity.
* Rendered delta `0`.
* `quality_state` / `publish_state` delta `0`.
* Browser/Wiki surface delta `0`.
* Branch B only: enum-token-only hash delta classification.
* Branch B only: chunk manifest and chunk file before/after hash delta classification.

Intended closeout ceiling:

* Complete: Branch A or Branch B plus all hard gates pass.
* Partial: Branch C or explicitly deferred runtime-facing rename.

---

## 1. Objective

이번 execution plan의 목적은 DVF 3-3 `runtime_state` vocabulary remap 이후 deferred 상태로 남은 runtime/static payload layer의 enum rename scope를 inventory-first 방식으로 확정하고, 가능한 경우 current operational artifact의 enum을 `adopted/unadopted`로 통일하는 것이다.

Current canonical target:

```text
runtime_state canonical enum = adopted / unadopted
legacy active / silent = historical/import/diagnostic alias only
current writers must not emit active / silent
historical sealed decision bodies are not rewritten
rendered text, Lua behavior, Browser/Wiki visibility, quality_state, publish_state remain invariant
```

This round closes the question:

```text
Which payload surfaces are eligible for active/silent -> adopted/unadopted rename,
which surfaces must remain historical/read-only,
and which runtime-facing surfaces, if any, require a separate baseline decision?
```

Expected closeout targets:

| Target | Meaning |
|---|---|
| PASS | canonical enum scope sealed, selected payload surfaces migrated, legacy alias read-only boundary sealed, rendered/Lua behavior/Browser-Wiki/quality/publish evidence-bounded parity proven |
| PARTIAL | scope matrix sealed, but runtime Lua payload rename is deferred because hash/smoke risk requires a separate round |
| BLOCKED | authority surfaces cannot be separated, or hash delta cannot be explained as enum-token serialization only |

---

## 2. Scope

This round is an operational payload contract cleanup and scope-seal round. It is not a runtime behavior round, quality/publish migration round, deployed closeout, or release readiness round.

In scope:

* Repository-wide inventory of `active`, `silent`, `adopted`, and `unadopted` literals.
* Classification of every `active/silent` occurrence into:

```text
operational current
frozen historical trace
test golden / fixture
  - current expected output baseline
  - historical authority body / frozen fixture
supporting trace
false positive / non-runtime_state meaning
```

* Surface disposition assignment:

```text
canonical_rename
legacy_alias_read_only
preserve_historical
forbidden_surface
informational_supporting_trace
false_positive
```

* Phase 1 branch decision:

| Branch | Meaning | Disposition |
|---|---|---|
| A | all in-scope surfaces are enum-internal-only | proceed with writer/validator rename; runtime-facing Phase 4 is no-op |
| B | some runtime-facing artifacts serialize the enum | rename in-scope runtime-facing serialization and seal a new enum-token-only baseline |
| C | runtime-facing serialization is too broad/risky for this round | close with inventory and deferred scope only |
| D | historical sealed body rewrite | rejected before execution |

* Single-writer sequencing:

```text
decision stage writer output enum
  -> validator / intermediate consumer enum
  -> bridge / runtime-facing artifact enum only if Branch B
```

* Default validator path realignment to canonical enum.
* Default validator input-source classification before validator fail-loud claims are made.
* Diagnostic/import/historical path preservation of legacy alias as read-only warning/report behavior.
* Dual-zero gate definition and execution:

```text
static residue count = 0 for in-scope operational current active/silent literals
dynamic execution reach count = 0 for current writer/validator/consumer paths emitting or consuming active/silent
```

* Round-local artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/
```

* Closeout documentation addenda after gates pass:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Branch C mutation stop:

```text
Branch C selection stops Change 2, Change 3, and Change 4 mutation.
Branch C closeout is inventory seal + deferred scope definition + partial closeout only.
Writer, validator, fixture, generated artifact, and runtime Lua mutation are prohibited under Branch C.
Branch C is a valid partial closeout, not a failed implementation.
```

### Explicitly Out Of Scope

* Historical sealed decision body direct rewrite.
* `runtime_state` semantic redefinition.
* `quality_state` or `publish_state` vocabulary migration.
* `adopted` reinterpretation as quality pass.
* `unadopted` reinterpretation as deletion, hidden state, Browser non-exposure, or quality failure.
* `runtime_state` reserved slot addition.
* `not_emitted`, `quality_exposed`, or other inactive reserved value activation.
* Runtime behavior change.
* Browser/Wiki UI policy change.
* Rendered text regeneration or sentence edits.
* Lua chunk topology redesign.
* Active monolith/chunks simultaneous deployment.
* Compose authority migration or redefinition.
* Silent/unadopted 21 row remediation.
* Source expansion, identity_fallback reassessment, role_fallback reassessment.
* Runtime Lua regeneration as a release/deploy claim.
* Manual in-game QA pass, runtime rollout, Workshop release, or `ready_for_release` declaration.
* External mod compatibility sweep.
* Pulse Core / Echo / Fuse / Nerve / Frame / Canvas impact.

---

## 3. Non-Goals

This plan does not attempt to:

* Reopen the 2026-04-26 docs-only `runtime_state` vocabulary remap decision.
* Remove the terminology migration note.
* Rewrite historical documents from `active/silent` to `adopted/unadopted`.
* Treat legacy `active/silent` diagnostic/import alias support as current writer permission.
* Collapse runtime_state, quality_state, and publish_state into one status model.
* Change row adoption counts.
* Change `primary_use`, body content, rendered output, facts, body_plan content, or source semantics.
* Promote any unadopted row to adopted.
* Reopen adapter / diagnostic final disposition or residual resolver compatibility debt.
* Reopen silent 21 metadata cleanup, which is already closed as its own Branch B cleanup round.
* Claim runtime equivalence beyond the evidence collected by this round.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` is the top authority.
* Latest `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md` readpoints are authoritative.
* The current docs/current readpoint already uses `adopted/unadopted`.
* Historical sealed decision bodies may contain `active/silent` and are read through the terminology migration note.
* Historical sealed decision bodies are read-only for this round.
* The 2026-04-26 docs-only vocabulary remap did not rewrite runtime/static payloads.

Baseline assumptions:

```text
row_count = 2105
adopted_count = 2084
unadopted_count = 21
previous active_count = 2084
previous silent_count = 21
quality_state values = strong / adequate / weak
publish_state values = internal_only / exposed
```

Architecture assumptions:

* `runtime_state`, `quality_state`, and `publish_state` remain separate axes.
* Decision stage remains the single writer for quality/publish/runtime state decisions.
* Validator, linter, bridge, and runtime consumer are not state writers.
* Default compose authority remains `compose_profiles_v2.json + body_plan`.
* Chunk manifest + chunk files remain runtime Lua deployable authority.
* Legacy alias consumption is allowed only in explicit diagnostic/import/historical read-only modes.
* Supporting artifacts such as AI-trace, debug logs, and observer outputs are not authority surfaces.

Environment assumptions:

* Windows PowerShell is the execution shell.
* Repository inspection uses `rg`, `fd`, `jq`, `git diff --stat`, and `git diff` when available.
* Validation results are claimable only when the exact relevant command exits with code `0`.

---

## 5. Repository Areas Affected

### Code

Expected in-scope code areas after Phase 1 confirms exact paths:

```text
Iris/build/description/v2/tools/build/**
Iris/build/description/v2/tests/**
```

Potential Branch B-only runtime-facing areas:

```text
Iris/**/media/lua/client/Iris/**
```

The exact writer, validator, intermediate consumer, bridge, and runtime-facing files must be resolved by Phase 1 inventory. No code path is mutation-authorized until it appears in `phase1_surface_inventory.json`.

### Docs

```text
docs/Iris/iris-dvf-3-3-runtime-payload-enum-rename-scope-round-plan.md
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Top-doc updates happen only in Phase 8 and must be addendum-only.

### Config

No config mutation is planned.

Read-only authority/config-like inputs may include:

```text
Iris/build/description/v2/**/compose_profiles_v2.json
Iris/build/description/v2/**/body_plan*
```

Exact paths are determined by Phase 1 and must not be redefined by this round.

### Generated Artifacts

Round-local staging root:

```text
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/
```

Common expected deliverables:

```text
phase1_surface_inventory.json
phase1_invariance_audit.json
phase1_branch_decision.json
phase2_writer_diff.json
phase2_writer_output_invariant_report.json
phase3_consumer_diff.json
phase3_test_suite_report.json
phase4_noop_report.json
phase4_new_baseline_seal.json
phase4_invariant_verification_report.json
phase5_static_residue_report.json
phase5_dynamic_reach_report.json
phase5_supporting_artifact_residue_inventory.json
phase6_hard_gate_report.json
phase7_adversarial_review.md
phase8_closeout_seal.json
runtime_payload_enum_rename_scope_round_closeout.json
runtime_payload_enum_rename_scope_round_closeout.md
legacy_alias_policy.json
```

Branch-specific deliverables:

* Branch A produces `phase4_noop_report.json`.
* Branch A also produces an explicit no-op `payload_enum_delta_report.json` with `runtime_facing_delta = 0`.
* Branch B produces `phase4_new_baseline_seal.json`, `payload_enum_delta_report.json`, and `runtime_surface_parity_report.json`.
* Branch C does not enter mutation phases and closes with deferred-scope artifacts, including `deferred_surface_followup_plan.json`.

Closeout artifact authority:

* `runtime_payload_enum_rename_scope_round_closeout.json` is the machine-readable closeout authority artifact.
* `runtime_payload_enum_rename_scope_round_closeout.md` is the human-readable closeout summary.
* `phase8_closeout_seal.json` is the Phase 8 gate trace that proves top-doc addenda and closeout artifact creation happened under the approved branch.

---

## 6. Planned Changes

### Phase 2-4 Mutation Gate

Branch C selection stops all mutation phases:

```text
Branch C selected -> Change 2, Change 3, and Change 4 do not run
Branch C closeout -> inventory seal + deferred scope definition + partial closeout
writer mutation -> prohibited
validator mutation -> prohibited
fixture/golden mutation -> prohibited
generated artifact mutation -> prohibited
runtime Lua mutation -> prohibited
```

Branch C is a valid partial closeout when Phase 1 proves that runtime-facing serialization, consumer comparison dependency, manifest authority handling, or hash/smoke risk cannot be safely handled inside this round.

### Change 1 - Phase 1 surface inventory and invariance audit

Purpose:

Establish the complete `active/silent` and `adopted/unadopted` occurrence map before any mutation, then classify each occurrence by authority surface, artifact lifecycle, and runtime exposure path.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase1_surface_inventory.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase1_invariance_audit.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase1_branch_decision.json
```

Implementation Notes:

* Use repository-wide literal search for `active`, `silent`, `adopted`, and `unadopted`.
* Use field-specific structured inspection for JSON/JSONL payloads where possible, such as `jq` queries over `runtime_state`, instead of treating every `active` string as a runtime_state occurrence.
* Separate docs, source JSON, generated JSON, writer code, validator code, tests, diagnostics, runtime Lua chunks, Browser/Wiki consumers, and supporting artifacts.
* Classify false positives where `active` is not `runtime_state`.
* Split test/golden fixtures into:

```text
current_expected_output_baseline = rename eligible
historical_authority_body_or_frozen_fixture = preserve historical
```

* Record generated artifact vs source authority distinction.
* Record Browser/Wiki, rendered text, Lua chunk, and bridge exposure path for each in-scope surface.
* Record validator input sources in `default_validator_input_sources`:

```text
[{source, type, legacy_emit_possibility}]
```

Allowed source classifications:

```text
writer-bound
external-bound
import-bound
diagnostic-bound
historical-bound
```

* Record Lua consumer comparison sites in `lua_consumer_enum_comparison_sites`:

```text
[{file, comparison_type, equivalent_rewrite_feasibility}]
```

* Record supporting artifacts as informational only unless they feed current writer, validator, consumer, or runtime paths. If a supporting artifact is consumed by a current authority path, reclassify it as operational current before Phase 1 closes.
* Record deferred follow-up round naming when Branch C or B3 is selected:

```text
follow_up_round_name = Iris DVF 3-3 <surface> Runtime Payload Enum Disposition Round
scope_inheritance = Phase 1 inventory + explicit deferred surface only
```

* Select Branch A, B, or C. Branch D is rejected by policy.

Validation:

```text
unclassified_active_silent_occurrence_count = 0
historical_body_mutation_target_count = 0
Browser_Wiki_surface_mutation_target_count = 0 unless Branch B explicitly proves enum serialization only
quality_state_target_count = 0
publish_state_target_count = 0
default_validator_input_sources_complete = true
lua_consumer_enum_comparison_sites_complete = true
test_golden_subclassification_complete = true
false_positive_runtime_state_exclusion_complete = true
row_count = 2105
adopted/unadopted baseline = 2084 / 21
baseline rendered hash recorded
baseline Lua/chunk hash recorded
```

---

### Change 2 - Phase 2 decision stage writer enum rewrite

Purpose:

Change the decision stage writer output for operational current artifacts from `active/silent` to `adopted/unadopted`, without allowing a transitional state where current writer output emits both vocabularies.

Files:

Exact files must be listed in `phase1_surface_inventory.json` before mutation. Expected file families:

```text
Iris/build/description/v2/tools/build/**
Iris/build/description/v2/tests/**
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase2_writer_diff.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase2_writer_output_invariant_report.json
```

Implementation Notes:

* Do not run Change 2 if Phase 1 selected Branch C.
* Limit code diff to enum literal output changes and immediately necessary fixture updates.
* Do not modify quality_state or publish_state logic.
* Do not modify row identity, rendered text, primary_use, body_plan, or compose authority.
* Do not introduce `not_emitted` or reserved runtime_state slots.
* Generated writer outputs must be produced through the approved writer path identified by Phase 1, not hand-edited.

Validation:

```text
writer output row_count = 2105
adopted_emit_count = 2084
unadopted_emit_count = 21
active_emit_count = 0
silent_emit_count = 0
writer code diff scope = enum literal change only
```

Run the relevant writer/output test command identified by Phase 1. If the whole Python suite is relevant at this phase, use:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

---

### Change 3 - Phase 3 validator and intermediate consumer realignment

Purpose:

Realign validators, intermediate JSON consumers, and downstream build-time consumers to canonical `adopted/unadopted` while preserving legacy alias only in explicit diagnostic/import/historical read-only modes.

Files:

Exact files must be listed in `phase1_surface_inventory.json`. Expected file families:

```text
Iris/build/description/v2/tools/build/**
Iris/build/description/v2/tests/**
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase3_consumer_diff.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase3_test_suite_report.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/legacy_alias_policy.json
```

Implementation Notes:

* Do not run Change 3 if Phase 1 selected Branch C.
* Default/current validation path must fail loud on `active/silent`.
* Diagnostic/import/historical validation path may consume `active/silent` only as legacy alias with report-only warning.
* `legacy_alias_policy.json` must classify every validator input source discovered in Phase 1 as one of:

```text
writer-bound
external-bound
import-bound
diagnostic-bound
historical-bound
```

* If default validator input is writer-bound only, `default path legacy enum fail` is a sentinel negative fixture and must be documented as such.
* If default validator input can be external-bound, the fail path is a real boundary check and must include a negative input fixture for that source.
* If both writer-bound and external-bound inputs exist, report and test each trigger path separately.
* Add or update report fields:

```text
legacy_alias_consumed_count
legacy_alias_surface
legacy_alias_mode
legacy_alias_input_source
legacy_alias_path_classification
```

* Keep validator as drift checker / gate, not writer.
* Cross-check enum-as-dict-key, filename, report schema, and fixture usage from Phase 1.

Validation:

```text
canonical enum pass
default path legacy enum fail, with source classified as sentinel or real boundary check
diagnostic/import alias path report-only pass
writer output accepted by validator
intermediate consumer row_count = 2105
intermediate consumer adopted/unadopted = 2084 / 21
default_validator_input_source_coverage = complete
```

Full suite target:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Expected baseline claim is `386 tests / OK` only if that exact command exits `0`.

---

### Change 4 - Phase 4 runtime-facing artifact disposition

Purpose:

Execute the Branch A/B/C decision from Phase 1 without changing runtime behavior or Browser/Wiki visibility.

Files:

Branch A:

```text
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase4_noop_report.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase4_invariant_verification_report.json
```

Branch B:

```text
Iris/**/media/lua/client/Iris/**
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase4_new_baseline_seal.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase4_invariant_verification_report.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/runtime_surface_parity_report.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/payload_enum_delta_report.json
```

Branch C:

```text
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase1_branch_decision.json
runtime-facing rename deferred to named follow-up round
```

Implementation Notes:

* Do not run Change 4 if Phase 1 selected Branch C.
* Branch A is no-op for runtime-facing artifacts.
* Branch B may change serialized enum tokens only where Phase 1 proves the surface is in scope.
* Branch B has three required sub-branches:

| Sub-branch | Condition | Disposition |
|---|---|---|
| B1 | `lua_consumer_enum_comparison_sites` count is `0` | serialized enum tokens may change; consumer code remains unchanged |
| B2 | comparison sites exist and every site is equivalent-rewrite feasible | serialized enum tokens and consumer comparison literals may change together; diff remains enum-literal only |
| B3 | indirect dependency exists or any site is not equivalent-rewrite feasible | downgrade to Branch C or split a named follow-up round |

* Phase 1 must decide B3 disposition before any mutation:
  * Downgrade to Branch C when the B3 finding blocks safe in-round mutation for the runtime-facing surface as a whole, lacks an approved generator/manifest writer path, requires behavior-policy work beyond enum literal equivalence, or makes Phase 6 parity unfalsifiable.
  * Split a named follow-up round when the B3 finding is a bounded runtime-facing sub-surface that can be isolated while current writer/validator scope remains safe and all non-deferred surfaces still satisfy Branch A/B invariants.
  * The selected B3 disposition must be recorded in `phase1_branch_decision.json` with the deferred surface, reason, and follow-up round name if split.
* Branch B runtime-facing mutation is allowed only if Phase 1 proves B1 or B2.
* Branch B chunk manifest handling:
  * If enum serialization changes any chunk file hash, the chunk manifest hash update is Branch B in scope.
  * The single writer for chunk files and chunk manifest is the approved runtime artifact/chunk manifest generator path identified by Phase 1.
  * If no approved generator/writer path exists for the manifest update, Branch B is not allowed and the affected surface moves to Branch C or a named follow-up.
  * Manifest updates must preserve chunk topology, deployable authority ownership, and active-monolith/chunks exclusion.
  * Manifest update is not a ROADMAP Hold violation only when the delta is generated by the approved path and classified as enum-token serialization only.
* `runtime_surface_parity_report.json` must include:

```text
manifest_before_hash
manifest_after_hash
chunk_file_hash_deltas[]
delta_classification = enum-token-only | other
chunk_manifest_authority_touched_outside_enum_token_serialization_count
```

* If a normalizer is introduced, it must be a single function and only map:

```text
active -> adopted
silent -> unadopted
```

* Unknown enum values must fail loud or produce explicit diagnostic error.
* Any Branch B normalizer must be closed as a bounded migration helper or moved to a documented diagnostic/import compatibility path. It must not become silent default compatibility authority.
* Do not change Lua consumer behavior, chunk topology, rendered text, visibility policy, or deployable authority ownership.

Validation:

```text
Branch A: staged Lua hash delta = false
Branch B: hash delta is explicit and enum_token_serialization_only = true
chunk manifest integrity verified
chunk_manifest_authority_touched_outside_enum_token_serialization_count = 0
Branch B sub-branch = B1 or B2
runtime parser smoke pass
Browser list smoke pass
Wiki panel smoke pass
rendered text delta = 0
```

Lua syntax validation if runtime Lua is touched:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

---

### Change 5 - Phase 5 static and dynamic residue audit

Purpose:

Prepare the hard gate by proving there is no remaining in-scope operational current `active/silent` static residue and no current execution path that emits or consumes legacy enum values.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase5_static_residue_report.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase5_dynamic_reach_report.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase5_supporting_artifact_residue_inventory.json
```

Implementation Notes:

* Static residue scan excludes frozen historical trace only after Phase 1 classification explicitly marks it as such.
* Static residue scan excludes Phase 1 false positives only after the false-positive reason and field/path evidence are recorded.
* Supporting artifact residue is recorded but not fail-loud unless it is consumed by a current authority path.
* Dynamic reach must cover writer, validator, intermediate consumer, and Branch B runtime-facing paths if applicable.
* Dynamic reach measurement method is:
  * run the approved writer/validator/consumer pipeline with instrumented counters or explicit report counters for emitted and consumed enum values;
  * run negative validator fixtures for each `default_validator_input_sources` path classification that can reach the default path;
  * when all default validator input sources are writer-bound only, reuse the Phase 3 sentinel legacy enum negative fixture as the Phase 5 validator negative fixture rather than creating a separate second fixture;
  * run Branch B runtime parser/smoke checks when runtime-facing artifacts are touched;
  * compare emitted/consumed enum counters against Phase 1 static inventory and Phase 2/3 reports.
* Static call graph review alone is insufficient for `dynamic_*_reach_count = 0`.
* If instrumentation or report counters cannot be added without exceeding enum-literal scope, report `blocked_dynamic_reach_method_missing` instead of claiming pass.

Validation:

```text
in_scope_operational_current_active_literal_count = 0
in_scope_operational_current_silent_literal_count = 0
dynamic_active_emit_or_consume_reach_count = 0
dynamic_silent_emit_or_consume_reach_count = 0
supporting residue inventory complete
dynamic_reach_measurement_method = instrumented counters or explicit report counters
```

---

### Change 6 - Phase 6 hard gate and Phase 7 adversarial review

Purpose:

Close the rename execution only if the dual-zero invariant, surface parity, and sealed boundary constraints all hold. Then perform adversarial review against the gate outputs.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase6_hard_gate_report.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase7_adversarial_review.md
```

Implementation Notes:

* Phase 6 failure stops the round. Do not proceed to closeout on a failed hard gate.
* Phase 7 must review branch selection, single-writer sequencing, 3-classification boundary, terminology note permanence, existing sealed boundary preservation, and validator dual-path separation.
* Phase 7 reject severity tiers:
  * Critical reject: inventory gap, wrong branch, unclassified surface, historical mutation risk, or dynamic reach method gap. Return to Phase 1.
  * Important reject: hard-gate evidence incomplete or stale. Revise evidence and rerun Phase 6.
  * Minor reject: wording or closeout trace issue with no invariant impact. Fix before Phase 8 closeout.

Validation:

```text
Phase 5 dual-zero = pass
row_count = 2105
adopted/unadopted = 2084 / 21
quality_state_delta = 0
publish_state_delta = 0
rendered_delta_count = 0
Browser_Wiki_surface_delta = 0
default_writer_legacy_emit_count = 0
default_validator_legacy_accept_count = 0
chunk_manifest_authority_touched_outside_enum_token_serialization_count = 0
terminology migration note remains permanent
historical_body_direct_rewrite_count = 0
runtime rollout / deployed closeout / Workshop release / ready_for_release claim count = 0
```

Full Python suite:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

---

### Change 7 - Phase 8 closeout and sealing

Purpose:

Record the selected branch, canonical enum scope, legacy alias policy, validation evidence, and non-decisions in top-level governance docs using addendum-only patches.

Files:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/phase8_closeout_seal.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/runtime_payload_enum_rename_scope_round_closeout.json
Iris/build/description/v2/staging/compose_contract_migration/runtime_payload_enum_rename_scope_round/runtime_payload_enum_rename_scope_round_closeout.md
```

Implementation Notes:

* `DECISIONS.md` addendum records selected branch, canonical enum, legacy alias policy, historical body rewrite prohibition, evidence, and non-decisions.
* `ARCHITECTURE.md` addendum records runtime_state enum contract, writer/validator/runtime consumer boundary, and diagnostic alias boundary.
* `ROADMAP.md` addendum updates Done/Doing/Hold and registers any deferred surface as a named follow-up round.
* `legacy_alias_policy.json` is a sealed evidence artifact referenced from the `DECISIONS.md` addendum. Its long-term governance ownership is the closeout decision, not an active default compatibility contract.
* `runtime_payload_enum_rename_scope_round_closeout.json` is the closeout authority artifact; `phase8_closeout_seal.json` is the Phase 8 execution trace.
* Deferred follow-up naming convention:

```text
Iris DVF 3-3 <surface> Runtime Payload Enum Disposition Round
```

* Deferred follow-up scope inheritance is limited to Phase 1 inventory evidence plus the explicitly deferred surface. It must not inherit mutation permission for unrelated writer, validator, fixture, or runtime Lua surfaces.
* Top-doc changes must not rewrite historical bodies.

Validation:

```text
top_doc_update_mode = addendum_only
historical_body_direct_rewrite_count = 0
deferred_surface_followup_registered = true if Branch C or partial Branch B
legacy_alias_policy_registered_as_closeout_evidence = true
closeout_json_authority_relationship_declared = true
claim_boundary_preserved = true
```

---

## 7. Validation Plan

### Automated Validation

Required validation commands and checks are selected by phase and must be reported with exact command, exit code, and result.

Core commands:

```powershell
rg "active|silent|adopted|unadopted" .
jq <field-specific runtime_state queries selected by Phase 1> <json/jsonl files>
git diff --stat
git diff
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Lua validation if any Lua runtime-facing file changes:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Required generated reports:

```text
phase1_surface_inventory.json
phase1_invariance_audit.json
phase1_branch_decision.json
phase2_writer_output_invariant_report.json
phase3_test_suite_report.json
phase4_invariant_verification_report.json
phase5_static_residue_report.json
phase5_dynamic_reach_report.json
phase6_hard_gate_report.json
phase7_adversarial_review.md
legacy_alias_policy.json
```

Branch B required generated reports:

```text
runtime_surface_parity_report.json
payload_enum_delta_report.json
phase4_new_baseline_seal.json
```

Automated invariant targets:

```text
unclassified_active_silent_occurrence_count = 0
default_validator_input_sources_complete = true
lua_consumer_enum_comparison_sites_complete = true
row_count = 2105
adopted_count = 2084
unadopted_count = 21
active_emit_count = 0
silent_emit_count = 0
quality_state_delta = 0
publish_state_delta = 0
rendered_delta_count = 0
Browser_Wiki_surface_delta = 0
chunk_manifest_authority_touched_outside_enum_token_serialization_count = 0
historical_body_direct_rewrite_count = 0
```

### Manual Validation

Manual validation is limited to smoke and review surfaces required by Branch B or by hard-gate evidence:

* Branch decision review.
* Writer diff scope review.
* Validator dual-path review.
* Rendered text delta inspection.
* Lua/chunk hash delta classification.
* Browser list smoke check if Branch B touches runtime-facing payload.
* Wiki panel smoke check if Branch B touches runtime-facing payload.

Manual in-game QA is not part of this plan.

### Validation Limits

This execution does not perform:

* Multiplayer validation.
* Deployment validation.
* Long-session runtime validation.
* External ecosystem compatibility sweep.
* Full release checklist.
* In-game QA pass.
* Workshop release readiness validation.
* Runtime rollout validation.
* Compatibility preservation validation for third-party mod extension surfaces.

---

## 8. Risk Surface Touch

### Authority Surface

Touched in planning and closeout docs. The decision stage writer may be touched after Phase 1 proves the exact operational current surface. Historical sealed decision bodies are not mutation targets.

### Runtime Behavior Surface

Expected unchanged. Branch A leaves runtime-facing artifacts unchanged. Branch B may change serialized enum tokens only after Phase 1 proves B1 or B2 feasibility and Phase 6 provides evidence-bounded runtime behavior and Browser/Wiki parity.

### Compatibility Surface

Default/current path becomes stricter: `active/silent` must fail loud outside diagnostic/import/historical modes. Diagnostic/import/historical alias support is compatibility read-only and must not become writer permission.

### Sealed Artifact Surface

Historical sealed decision bodies are preserve-historical. Test golden/fixture updates are allowed only when Phase 1 classifies them as current expected output baselines, not historical authority bodies or frozen fixtures.

### Public-Facing Output Surface

Rendered text, Browser/Wiki visibility, tooltip/wiki content, and public runtime behavior are expected unchanged. Any public-facing delta fails the round unless Phase 1 explicitly routes the round to Branch C before mutation.

---

## 9. Risk Analysis

### Architecture Risk

* `runtime_state` rename could accidentally bleed into `quality_state` or `publish_state` semantics.
* A normalizer introduced for Branch B could become a permanent compatibility adapter rather than a bounded migration helper.
* Generated artifact and source authority could be confused, causing mutation of the wrong surface.
* Branch decision could be made from incomplete inventory if grep results are not fully classified.

### Runtime Risk

* Lua consumer code may compare `active/silent` directly.
* Runtime-facing serialized enum values may affect bridge parsing or UI filtering indirectly.
* Branch B hash changes could be broader than enum-token serialization.
* Chunk manifest/chunk file authority could be disturbed if runtime-facing artifacts are regenerated too broadly.
* Branch B must downgrade to Branch C if consumer comparison sites cannot be equivalently rewritten or if manifest updates cannot be generated by the approved writer path.

### Compatibility Risk

* Default validator strictness could reject historical/import fixtures if diagnostic path separation is incomplete.
* Legacy alias read-only support could be misread as current writer compatibility.
* External mod extension surfaces are not swept in this round.

### Regression Risk

* Writer diff could accidentally change row count, row identity, body content, quality_state, or publish_state.
* Test golden updates could hide behavior changes if not tied to enum-only deltas.
* Supporting artifact residue could be incorrectly treated as fail-loud operational residue, or operational residue could be mislabeled as supporting trace.
* Documentation wording could imply `adopted = quality pass` or `unadopted = hidden/deleted`.

---

## 10. Rollback Plan

Phase 1 rollback:

* No code mutation is allowed. If inventory is incomplete, revise Phase 1 artifacts and rerun inventory.

Phase 2-3 rollback:

* Revert writer, validator, consumer, and fixture changes with normal git revert/patch rollback.
* No baseline rebaseline is expected before Phase 4.

Phase 4 Branch B rollback:

* Before new baseline seal: revert artifact/code changes and return to Phase 1 branch decision.
* After new baseline seal: stop at Phase 6 hard gate failure, close the round as `closed_with_baseline_rollback_required`, and open a separate rollback round. Do not silently restore or overwrite sealed baselines.

Phase 5-6 rollback:

* Dual-zero or hard-gate failure stops closeout.
* Return to Phase 1 inventory and reclassify missed surfaces.

Phase 7 rollback:

* Adversarial reject blocks Phase 8.
* Critical reject returns to Phase 1.
* Important reject requires evidence revision and Phase 6 rerun.
* Minor reject may proceed only after wording/trace revision before Phase 8.

Historical body mutation rollback:

* Immediately revert the offending patch.
* Mark the round failed with `historical_body_rewrite_violation`.
* Restart with historical docs in an explicit read-only denylist.

---

## 11. Governance Constraints

Required constraints:

* `docs/Philosophy.md` compliance.
* Hub & Spoke boundary preservation.
* Iris-only scope; no Pulse Core / Echo / Fuse / Nerve / Frame / Canvas impact.
* Historical sealed decision body direct rewrite prohibition.
* Addendum-only top-doc closeout updates.
* Single-writer principle: decision stage is sole authority for state output.
* Validator remains checker/gate, not writer.
* Generated authoritative artifacts must be produced by approved writer/generator paths, not hand-edited; this restates the `Round Opening Disclosure` mutation responsibility as a governance constraint.
* Determinism: same input must produce same output except for intended enum-token rename.
* `runtime_state`, `quality_state`, and `publish_state` remain separate axes.
* `runtime_state` reserved slot addition prohibited.
* `not_emitted` adoption prohibited.
* `quality_exposed` activation prohibited.
* `adopted` must not mean quality pass.
* `unadopted` must not mean deletion, suppression, Browser non-exposure, or quality failure.
* Compose authority remains `compose_profiles_v2.json + body_plan`.
* Chunk manifest + chunk files remain deployable authority, and Branch B may update their hashes only through the approved generator path with enum-token-only delta classification.
* Active monolith/chunks simultaneous deployment prohibited.
* Baseline row count and split remain `2105 / 2084 / 21`.
* Rendered text change prohibited.
* Browser/Wiki exposure policy change prohibited.
* Closeout claims are evidence-bounded and do not imply runtime rollout, deployed closeout, Workshop readiness, in-game QA pass, or `ready_for_release`.
* Terminology migration note remains permanent after this round.

---

## 12. Expected Closeout State

Expected closeout is `complete` only if Phase 1 selects Branch A or Branch B and all hard gates pass.

Complete closeout:

```text
closed_with_runtime_payload_enum_scope_sealed
canonical runtime_state enum = adopted / unadopted
current writers emit no active/silent
legacy active/silent alias = historical/import/diagnostic read-only only
in-scope operational current active/silent residue = 0
dynamic current active/silent reach = 0
row_count = 2105
adopted/unadopted = 2084 / 21
rendered/Lua behavior/Browser-Wiki/quality_state/publish_state evidence-bounded parity proven
parity claim boundary = Phase 6 validation only
```

Partial closeout:

```text
Branch C:
  closed_with_runtime_payload_scope_matrix_sealed_and_runtime_facing_rename_deferred

Branch B deferred sub-scope:
  closed_with_runtime_payload_scope_matrix_sealed_and_named_followup_required
```

Use Branch C partial closeout when Phase 1 selects Branch C before mutation. Use Branch B deferred sub-scope partial closeout when Branch B starts from B1/B2 eligibility but discovers a bounded hash/smoke/manifest/consumer sub-surface that should be split into a separate disposition round before hard-gate closeout.

Blocked closeout:

```text
blocked_unclassified_authority_surface
blocked_unexplained_hash_delta
blocked_historical_body_rewrite_violation
blocked_dual_zero_gate_failure
blocked_dynamic_reach_method_missing
```

Non-claims at closeout:

* No runtime rollout.
* No deployed closeout.
* No Workshop release readiness.
* No in-game QA pass.
* No `ready_for_release`.
* No termination of terminology migration note.
* No historical decision body vocabulary cleanup.
