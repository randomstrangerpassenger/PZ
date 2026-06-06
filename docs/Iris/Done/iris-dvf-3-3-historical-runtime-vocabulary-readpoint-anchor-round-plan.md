# Iris DVF 3-3 Historical Runtime Vocabulary Readpoint Anchor Round Plan

> 상태: Draft v0.3-review-2-applied
> 기준일: 2026-05-25
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP - Iris DVF 3-3 Historical Runtime Vocabulary Readpoint Anchor Round (Synthesis)` (2026-05-25 user-provided synthesis)
> review input: `REVIEW - Iris DVF 3-3 Historical Runtime Vocabulary Readpoint Anchor Round (Synthesis)` WARN feedback (2026-05-25), R1 through R10 incorporated in v0.2.
> review input: `REVIEW - Iris DVF 3-3 Historical Runtime Vocabulary Readpoint Anchor Round Plan (v0.2-review-applied)` WARN feedback (2026-05-25), authoritative-doc promotion ordering, central-anchor/addendum integration, unknown-gate proportionality, path preflight, and prohibited-touch wording incorporated in v0.3.
> 근거 readpoint: `DECISIONS.md` latest-readpoint rule, `2026-04-26 runtime_state vocabulary remapped`, `2026-05-21 GUARD-A`, `ARCHITECTURE.md` current Iris DVF 3-3 readpoints.
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`; the template is a project planning form under `docs/`, not semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.
> 실행 상태: planning authority only. 이 문서는 historical/provenance `active/silent` readpoint anchor round를 열기 위한 실행 계획이며, 작성 시점에는 runtime Lua, generated runtime artifacts, sealed historical bodies, fixture bodies, staging artifact bodies, source decisions, rendered text, deployed state, release state, or closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 DVF 3-3 historical / diagnostic / import / fixture / staging / Done-doc surface에 남아 있는 legacy `active/silent` vocabulary가 current runtime authority로 오독되지 않도록 readpoint anchor를 추가형으로 봉인하는 것이다.

핵심 objective:

```text
historical active/silent must remain preserved where it belongs
historical active/silent must not be read as current runtime authority
current runtime payload authority remains adopted/unadopted
GUARD-A remains owner of current-surface re-entry prevention
anchor remains reader-facing governance output, not a machine-enforced guard
repo-wide active/silent lexical zero is not a success criterion
sealed historical bodies, fixtures, staging artifact bodies, and hash-sealed artifacts must not be rewritten
```

이번 round의 검증 질문은 다음 하나로 제한한다.

```text
남아 있는 active/silent occurrence가 current authority인지 아닌지 분류되고,
in-scope historical/provenance surface가 adopted/unadopted canonical readpoint로
오독 없이 연결되었는가?
```

성공 시 최대 선언 가능 범위:

```text
historical active/silent readpoint anchored as non-current authority vocabulary
current runtime authority remains adopted/unadopted
GUARD-A ownership preserved
reader-facing anchor installed without creating a new guard
```

성공해도 선언 금지:

```text
repo-wide active/silent zero
diagnostic/import/historical alias removal
legacy enum migration rerun
GUARD-A redefinition or strengthening
runtime rollout
deployed closeout
manual in-game QA pass
Workshop readiness
ready_for_release
runtime equivalence
```

Anchor status boundary:

```text
anchor는 reader-facing 거버넌스 산출물이며 기계 강제 guard가 아니다.
current-label fail-loud 강제는 오직 GUARD-A가 담당한다.
```

---

## 2. Scope

This round is a documentation-governance and readpoint-anchor round. It inventories remaining `active/silent` occurrences, classifies their authority status, fixes the anchor note contract, makes a governed placement decision, stages additive readpoint anchor drafts, verifies negative invariants, passes adversarial review, and only then promotes evidence-bounded addenda to live governance docs.

In scope:

* Scope lock for `Iris DVF 3-3 Historical Runtime Vocabulary Readpoint Anchor Round`.
* Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/
```

* Phase 1 scope and surface manifests:

```text
phase1_scope_lock/readpoint_scope_manifest.json
phase1_scope_lock/immutable_surface_manifest.json
phase1_scope_lock/mutable_surface_manifest.json
phase1_scope_lock/historical_runtime_vocabulary_anchor_surface_inventory.json
phase1_scope_lock/hash_sealed_identity_manifest.json
```

* Phase 2 occurrence inventory for lexical and contextual `active/silent` variants:

```text
phase2_occurrence_inventory/active_silent_occurrence_inventory.jsonl
phase2_occurrence_inventory/authority_relevant_occurrence_inventory.jsonl
phase2_occurrence_inventory/bare_token_secondary_audit.jsonl
phase2_occurrence_inventory/occurrence_summary.json
```

* Phase 3 readpoint classification:

```text
phase3_readpoint_classification/classified_occurrence_inventory.jsonl
phase3_readpoint_classification/readpoint_classification_report.json
phase3_readpoint_classification/anchor_target_manifest.json
```

* Phase 4 anchor contract and placement governance disposition:

```text
phase4_contract_and_placement_disposition/anchor_note_contract.md
phase4_contract_and_placement_disposition/placement_disposition_decision.md
```

* Phase 5 staged additive anchor drafts. These are round-local draft artifacts only; live governance docs are not written in Change 5:

```text
phase5_anchor_patch/anchor_patch_manifest.json
phase5_anchor_patch/anchor_patch_report.md
phase5_anchor_patch/staged_central_readpoint_anchor_draft.md
phase5_anchor_patch/staged_pointer_patch_drafts/
```

* Phase 6 hard gate evidence:

```text
phase6_hard_gate/negative_invariant_report.json
phase6_hard_gate/hard_gate_report.json
phase6_hard_gate/prohibited_mutation_report.json
phase6_hard_gate/runtime_surface_invariance_report.json
```

* Phase 7 adversarial review using `docs/REVIEW_TEMPLATE.md`.
* Phase 8 closeout report and addendum drafts:

```text
phase8_closeout/closeout_report.md
phase8_closeout/decisions_addendum.md
phase8_closeout/architecture_addendum.md
phase8_closeout/roadmap_addendum.md
```

Phase 8 is the only phase that may promote staged anchor/addendum text into live authoritative docs, and only after Change 6 hard gates and Change 7 adversarial review pass.

* Occurrence classification schema with at least:

```json
{
  "path": "...",
  "line": 123,
  "token": "active",
  "surface_class": "historical_done_doc",
  "readpoint_class": "historical_runtime_vocabulary",
  "current_authority": false,
  "allowed": true,
  "anchor_required": true,
  "mutation_allowed": false,
  "reason": "historical sealed body; active/silent are provenance vocabulary here"
}
```

* Surface classes:

```text
current_runtime_payload
current_writer_output
current_generated_report_operator_surface
packaged_lua_data
historical_decision_body
decisions_historical_trace
architecture_historical_trace
roadmap_addendum_ledger
done_doc
walkthrough
staging_artifact
fixture
hash_sealed_artifact
diagnostic_alias
import_alias
legacy_metric_key
test_fixture
unrelated_identifier
unknown
```

* Readpoint classes:

```text
current_authority_forbidden
historical_runtime_vocabulary
provenance_vocabulary
diagnostic_readonly_alias
import_readonly_alias
legacy_metric_nonlabel
test_fixture_non_authority
unrelated_identifier
unknown_blocker
```

* Placement target classes:

```text
central_current_readpoint_doc
editable_pointer_surface
sealed_historical_body_no_patch
fixture_or_staging_body_no_patch
readme_or_wrapper_pointer_allowed
hash_sealed_artifact_no_patch
```

* Optional scanner/validator helper only if it stays under the round-local staging root by default and does not duplicate GUARD-A ownership. Repo-level helper/test placement is allowed only if the execution explicitly classifies it as repo-level code/test mutation, runs the full relevant Python validation, and asserts that the helper is not a current-surface guard.

### Explicitly Out Of Scope

* Legacy enum migration rerun.
* Historical `active -> adopted` / `silent -> unadopted` body-wide replacement.
* Repo-wide `active/silent` lexical zero.
* Diagnostic/import/historical alias removal.
* Fixture deletion or fixture token replacement.
* Staging artifact body token replacement.
* Sealed decision body rewrite.
* Hash-sealed artifact byte mutation, including append-only header mutation on sha256-referenced files.
* Static Report Label Cleanup Referent Recovery Round reopening.
* GUARD-A reimplementation, redefinition, broadening, or ownership transfer.
* Runtime Lua mutation.
* Packaged Lua regeneration.
* Rendered text rebaseline.
* Source decisions row identity mutation.
* `runtime_state`, `quality_state`, or `publish_state` semantic mutation.
* Browser / Wiki / Tooltip runtime behavior change.
* Manual in-game QA pass.
* Deployed closeout.
* Runtime rollout.
* Workshop release readiness or `ready_for_release`.

---

## 3. Non-Goals

This plan does not attempt to:

* Remove every `active/silent` token from the repository.
* Treat remaining historical vocabulary as cleanup residue by lexical match alone.
* Convert historical `active` into a live synonym for current `runtime_state = adopted`.
* Convert historical `silent` into a live synonym for current `runtime_state = unadopted`.
* Rewrite path/hash-locked artifacts.
* Mutate any hash-sealed artifact whose sha256 is referenced by another decision, closeout, identity gate, or staging evidence manifest.
* Rewrite fixture or staging artifact bodies.
* Remove diagnostic/import/read-only aliases.
* Add a new current-surface guard beside GUARD-A.
* Move writer authority from the designated `adopted/unadopted` writer to documentation anchors.
* Claim current runtime payload, generated reports, packaged Lua, or writer output changed.
* Claim release, deployment, Workshop, B42, tooltip, or runtime equivalence readiness.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` remains the top authority.
* Iris remains a 100% Lua wiki-style module and must not absorb Pulse Core or other spoke responsibilities.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are current governance readpoints.
* `DECISIONS.md` latest-readpoint rule applies: later decisions are current authoritative readpoints; earlier entries remain historical trace.
* Current runtime payload canonical enum is `adopted/unadopted`, sealed by the 2026-04-26 runtime-state vocabulary remap.
* Legacy `active/silent` is allowed only as historical/provenance/diagnostic/import/read-only/test/non-authority vocabulary unless GUARD-A identifies a current-surface violation.

Runtime/state assumptions:

* Current 2105-row source decision identity is unchanged.
* Current split is `adopted 2084 / unadopted 21`.
* Runtime-facing Lua chunks already use current canonical payload where required.
* `runtime_state`, `quality_state`, and `publish_state` remain separate axes.
* Rendered text, runtime Lua, packaged Lua, source decisions, row identity, and consumer behavior are immutable for this round.

Guard assumptions:

* GUARD-A owns future current-surface legacy `active/silent` re-entry prevention.
* GUARD-A hard-fail surfaces remain current runtime payload, current writer output, current generated report/operator output, and packaged Lua data.
* This round owns historical/provenance readpoint anchoring only.
* If the inventory finds `current_authority_forbidden`, this round does not fix it by historical anchor; it escalates to the existing GUARD-A path and blocks closeout.
* Phase 1 current-surface `(c)` tagging inherits and references the existing GUARD-A hard-fail / allow surface manifest as its single truth source. This round does not independently redefine that boundary; it layers only the historical anchor axis on top of GUARD-A's sealed surface ownership.

Validation assumptions:

* Prior observed validation baseline was Python unittest `394 / OK` and Lua syntax `183 files / OK`, but observed counts are not hard gates because unrelated test/file count changes can occur.
* The plan may require exact validation commands before closeout, but no validation is considered passed unless the exact relevant command exits with code `0`.
* If no executable code changes are made, Python/Lua validation may be recorded as invariance confirmation rather than behavior proof.

Path assumptions:

* Execution preflight must confirm `docs/PLAN_TEMPLATE.md` exists before relying on this plan form.
* Execution preflight must confirm these governance docs exist before preparing live patches:

```text
docs/Philosophy.md
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

---

## 5. Repository Areas Affected

### Code

* None by default.
* Preferred optional scanner/validator location, if Phase 2-6 need one:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/tools/<round-local-helper>.py
```

If a helper or test must be promoted to repo-level code/test paths such as `Iris/build/description/v2/tools/build/**` or `Iris/build/description/v2/tests/**`, the execution must:

```text
classify the change as repo-level code/test mutation
run the full relevant Python validation
state that the helper is documentation-governance support only
state that the helper is not GUARD-A and not a current-surface guard
```

Any helper must stay documentation-governance oriented and must not duplicate GUARD-A current-surface ownership.

### Docs

Planning doc:

```text
docs/Iris/iris-dvf-3-3-historical-runtime-vocabulary-readpoint-anchor-round-plan.md
```

Potential closeout addenda after gates pass only:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Potential additive pointer surfaces only if Phase 4 selects placement option B and the target is classified as `editable_pointer_surface`:

```text
docs/Iris/Done/**
docs/Iris/Done/Walkthrough/**
docs/Iris/Done/plan/**
```

### Config

* None.

### Generated Artifacts

Round-local documentation-governance evidence only:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/**
```

No runtime generated artifact is in scope.

---

## 6. Planned Changes

### Change 1

Purpose:

Seal the round boundary before occurrence scanning, including what this round may and may not mutate.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase1_scope_lock/readpoint_scope_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase1_scope_lock/immutable_surface_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase1_scope_lock/mutable_surface_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase1_scope_lock/historical_runtime_vocabulary_anchor_surface_inventory.json
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase1_scope_lock/hash_sealed_identity_manifest.json
```

Implementation Notes:

* Record that this is a readpoint anchor round, not enum migration or guard implementation.
* Seal immutable surfaces:

```text
historical sealed decision bodies
path/hash-locked artifacts
hash-sealed identity artifacts referenced by sha256 in decisions, closeouts, or downstream identity gates
current runtime Lua chunks
current runtime payload writer
source decisions row identity
rendered text
runtime_state / quality_state / publish_state semantics
Browser / Wiki / Tooltip runtime behavior
diagnostic/import/historical alias fixture body
staging artifact body
```

* Seal mutable surfaces:

```text
round-local staging inventory
readpoint classification manifest
docs-level anchor notes
closeout addenda
optional scanner/validator helper
```

* Add a `hash_sealed_identity` axis to the surface inventory. Each historical surface must be classified as exactly one of:

```text
hash_sealed_artifact_no_patch
append_tolerable_pointer_surface
non_file_or_excluded_surface
```

* For `hash_sealed_artifact_no_patch`, record path, source reference, pre-round sha256, reason for immutability, and downstream consumer if known.
* Record that placement option B is structurally forbidden for `hash_sealed_artifact_no_patch`; only wrapper README/pointer files may be used around those surfaces.
* Inherit GUARD-A hard-fail / allow surface boundaries for `(c) current surface` tagging. This round must reference the GUARD-A manifest as input and must not independently redefine hard-fail current authority surfaces.

* Record required flags:

```text
runtime_payload_mutation = false
historical_body_direct_rewrite = false
repo_wide_zero_gate = false
existing_current_surface_guard_owner = "GUARD-A"
guard_a_manifest_inherited_for_current_surface_boundary = true
```

Validation:

* Scope manifest contains all required negative flags.
* Immutable and mutable manifests do not overlap except through explicit read-only references.
* GUARD-A current-surface definition is referenced but not redefined.
* `hash_sealed_identity_manifest.json` records pre-round sha256 for every hash-sealed file in scope.
* No `hash_sealed_artifact_no_patch` file is present in a mutable placement target set.

---

### Change 2

Purpose:

Build a complete occurrence inventory for `active/silent` vocabulary and related legacy labels before any anchor is placed.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase2_occurrence_inventory/active_silent_occurrence_inventory.jsonl
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase2_occurrence_inventory/authority_relevant_occurrence_inventory.jsonl
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase2_occurrence_inventory/bare_token_secondary_audit.jsonl
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase2_occurrence_inventory/occurrence_summary.json
```

Implementation Notes:

* Search for:

```text
active
silent
"active"
"silent"
state = active
state = silent
active_composed
silent_metadata
active_count / silent_count and other legacy metric keys
```

* Include false positives rather than silently dropping them.
* Record path, line, context, token, initial surface guess, and exclusion reason if excluded.
* Keep binary/generated/irrelevant exclusions explicit and auditable.
* Current hard-fail surface findings are separated for GUARD-A escalation, not fixed by historical anchor.
* Split the inventory into two populations:

```text
authority_relevant_occurrence_inventory:
  Gate population. Includes runtime_state/source/payload/enum/report/operator/legacy metric key,
  diagnostic/import alias, historical quote/body, fixture, staging artifact, and other contexts
  that could plausibly be read as runtime-state vocabulary or current authority.

bare_token_secondary_audit:
  Non-gate audit population. Includes broad bare-token/common-word/code-identifier matches
  such as isActive, setActive, activeView, silent failure prose, and unrelated identifiers.
```

* Bare-token full sweep remains auditable, but it is not a repo-wide lexical zero gate and must not dominate closeout.

Validation:

* Inventory is valid JSONL.
* `authority_relevant_unknown_count` is recorded and must be `0` before anchor draft staging.
* `bare_token_sweep_unknown_count` is recorded as audit evidence but is not a hard gate unless a reviewer promotes a specific bare-token occurrence into the authority-relevant population.
* Exclusion rules are explicit and do not hide current-surface labels.

---

### Change 3

Purpose:

Classify every occurrence by current authority status and determine which surfaces need anchors.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase3_readpoint_classification/classified_occurrence_inventory.jsonl
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase3_readpoint_classification/readpoint_classification_report.json
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase3_readpoint_classification/anchor_target_manifest.json
```

Implementation Notes:

* Assign these booleans for every occurrence:

```text
current_authority
allowed
anchor_required
mutation_allowed
```

* `allowed = true` and `current_authority = false` must be valid together.
* In-scope historical/provenance occurrences become anchor candidates.
* Diagnostic/import alias occurrences are preserved as non-authority vocabulary, not cleanup targets.
* `current_authority_forbidden` blocks closeout and is escalated to GUARD-A.

Validation:

* `unknown_blocker = 0`.
* Every historical/provenance occurrence has `current_authority = false`.
* Every diagnostic/import alias has `writer_authority = false`.
* Every `anchor_required = true` occurrence maps to an anchor target or a documented blocker.

---

### Change 4

Purpose:

Fix the anchor note content contract and make the one unresolved placement branch a governed disposition before patching.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase4_contract_and_placement_disposition/anchor_note_contract.md
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase4_contract_and_placement_disposition/placement_disposition_decision.md
```

Implementation Notes:

The anchor note contract must state all of the following:

```text
active/silent on the anchored surface is historical/provenance/diagnostic/import vocabulary
active/silent on the anchored surface is not the current writer/runtime enum
current runtime payload authority is adopted/unadopted
historical active must not be read as live current runtime_state = adopted
current-label re-entry prevention remains owned by GUARD-A
sealed historical bodies are preserved and must not be rewritten for vocabulary cleanup
```

The contract must also state:

```text
the anchor does not instruct token replacement
the anchor does not remove diagnostic/import aliases
the anchor does not redefine GUARD-A
the anchor is reader-facing governance output, not a machine-enforced guard
```

Placement disposition must choose exactly one of:

```text
A. Central authoritative readpoint anchor only.
   Historical surfaces connect through DECISIONS latest-readpoint rule and ARCHITECTURE 9-2/current Iris DVF 3-3 readpoint.

B. Central anchor plus append-only pointers on editable historical docs / walkthroughs / fixture or staging README surfaces.
   Sealed body text, fixture tokens, staging artifact tokens, and hash-sealed artifact files remain untouched.
```

Placement disposition must classify each target with this enum before any patch:

```text
central_current_readpoint_doc         # central authoritative anchor placement target
editable_pointer_surface              # append-tolerable Done doc / walkthrough / plan surface
sealed_historical_body_no_patch       # no direct patch
fixture_or_staging_body_no_patch      # no direct patch
readme_or_wrapper_pointer_allowed     # wrapper pointer only around fixture/staging bodies
hash_sealed_artifact_no_patch         # sha256 referent; no direct patch
```

Option B may target only `editable_pointer_surface`, `readme_or_wrapper_pointer_allowed`, and the selected `central_current_readpoint_doc`. It must never target `sealed_historical_body_no_patch`, `fixture_or_staging_body_no_patch`, or `hash_sealed_artifact_no_patch`.

Implementation must not proceed to Change 5 until `placement_disposition_decision.md` is sealed.

Validation:

* Anchor contract is consistent with additive-only, alias preservation, and sealed-body non-rewrite constraints.
* Placement decision explains why the selected option does not violate historical body mutation rules.
* Placement decision explains how hash-sealed artifacts remain byte-identical.
* No anchor placement file is patched before this decision is recorded.

---

### Change 5

Purpose:

Stage readpoint anchor drafts additively according to the Phase 4 placement disposition. Change 5 does not write live authoritative governance docs.

Files:

Live central readpoint documents are not write targets in Change 5:

```text
docs/DECISIONS.md     # draft-only source/target reference; live write deferred to Change 8
docs/ARCHITECTURE.md  # draft-only source/target reference; live write deferred to Change 8
docs/ROADMAP.md       # draft-only source/target reference; live write deferred to Change 8
```

Additional pointer surfaces are draft-only in Change 5, even if Phase 4 selects option B:

```text
docs/Iris/Done/**             # draft-only target reference unless promoted in Change 8
docs/Iris/Done/Walkthrough/** # draft-only target reference unless promoted in Change 8
docs/Iris/Done/plan/**        # draft-only target reference unless promoted in Change 8
README or pointer files around fixture/staging surfaces selected by anchor_target_manifest
```

Round-local evidence:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase5_anchor_patch/anchor_patch_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase5_anchor_patch/anchor_patch_report.md
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase5_anchor_patch/staged_central_readpoint_anchor_draft.md
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase5_anchor_patch/staged_pointer_patch_drafts/
```

Implementation Notes:

* Prepare only append-only anchor or pointer note drafts.
* Do not write `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, or other live docs in Change 5.
* Live document promotion is deferred to Change 8 after Change 6 hard gates and Change 7 adversarial review pass.
* Stage drafts only according to the placement class sealed in Change 4.
* Do not edit historical body tokens, even in draft patches.
* Do not replace any `active/silent` occurrence.
* Do not prepare direct patch drafts for fixtures, staging artifact bodies, sealed historical bodies, or hash-sealed artifact files.
* Record before/after occurrence counts and explicitly state that lexical zero is not expected.
* Draft only targets listed in `anchor_target_manifest.json`.
* Central anchor and closeout addendum text are a single integrated dated readpoint draft, not two independent authoritative entries.

Validation:

* `historical_body_direct_rewrite_count = 0`.
* `fixture_token_changed = false`.
* `staging_artifact_token_changed = false`.
* `hash_sealed_artifact_sha256_unchanged = true`.
* `alias_removed = false`.
* `live_authoritative_doc_written_in_change5 = false`.
* `central_anchor_closeout_addendum_integrated = true`.
* Anchor text contains no enum migration rerun claim.
* Anchor text does not define a new runtime authority.

---

### Change 6

Purpose:

Prove negative invariants and hard gates before closeout addenda become authoritative.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase6_hard_gate/negative_invariant_report.json
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase6_hard_gate/hard_gate_report.json
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase6_hard_gate/prohibited_mutation_report.json
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase6_hard_gate/runtime_surface_invariance_report.json
```

Implementation Notes:

Expected negative invariant values:

```text
historical_body_direct_rewrite_count = 0
runtime_lua_changed = false
source_decisions_row_identity_changed = false
rendered_text_changed = false
runtime_state_semantics_changed = false
quality_state_semantics_changed = false
publish_state_semantics_changed = false
diagnostic_alias_removed = false
import_alias_removed = false
fixture_token_changed = false
staging_artifact_token_changed = false
hash_sealed_artifact_sha256_unchanged = true
repo_wide_active_silent_zero_claim = false
new_current_surface_guard_added = 0
guard_a_unchanged = true
guard_a_manifest_boundary_redefined = false
authority_relevant_unknown_count = 0
bare_token_sweep_unknown_count = "<actual, non-gate>"
current_authority_forbidden_count = 0
guard_a_escalation_required = false
anchor_required_unpatched_count = 0
touched_prohibited_lua_py_fixture_count = 0
live_authoritative_doc_written_before_change8 = false
central_anchor_closeout_addendum_integrated = true
python_unittest_command_exited_0 = true
python_unittest_failures = 0
python_unittest_observed_count = "<actual>"
lua_syntax_command_exited_0 = true
lua_syntax_failures = 0
lua_syntax_observed_count = "<actual>"
```

Hard gates:

```text
Gate A: anchor-required historical/provenance surfaces are connected to staged anchor drafts
Gate B: negative invariant values pass, including sha256 immutability for hash-sealed artifacts
Gate C: DECISIONS 2026-04-26, GUARD-A 2026-05-21, and ARCHITECTURE current readpoints remain consistent
Gate D: code suite invariance is confirmed when exact validation commands are run
Gate E: no live authoritative governance doc write occurred before gated Change 8 promotion
```

Validation:

* Reports are valid JSON or Markdown as applicable.
* No closeout addendum is applied if any hard gate fails.
* If exact Python/Lua commands are not run, the report marks validation as blocked or not-run, not passed.
* Test/file counts are observed facts, not fixed invariant values; pass/fail is determined by exit code `0` and failure count `0`.
* The pre/post sha256 set for `hash_sealed_artifact_no_patch` is compared and must be byte-identical.
* `authority_relevant_unknown_count = 0` is the hard gate; `bare_token_sweep_unknown_count` is audit evidence unless promoted into authority-relevant scope.
* Staged anchor drafts are reviewed, but live `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and optional pointer docs remain unchanged before Change 8.

---

### Change 7

Purpose:

Perform adversarial review before governance closeout.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase7_adversarial_review/adversarial_review.md
```

Implementation Notes:

* Use the actual `docs/REVIEW_TEMPLATE.md` 1-12 structure:

```text
1. Verdict
2. Executive Summary
3. Critical Issues
4. Non-Critical Issues
5. Scope Review
6. Validation Review
7. Governance Review
8. Risk Surface Review
9. Risk Review
10. Required Revisions
11. Final Recommendation
12. Reviewer Notes
```

* Review must specifically attack:

```text
whether active was accidentally made a synonym for current adopted
whether GUARD-A ownership was diluted
whether sealed body mutation happened
whether hash-sealed artifact sha256 changed
whether fixture/staging artifacts were silently rewritten
whether lexical zero was implied
whether closeout claims exceed evidence
```

Validation:

* Critical count is `0`.
* Verdict scale is `PASS / WARN / FAIL`.
* `PASS` is required for closeout.
* `WARN`, `FAIL`, or unresolved critical findings block closeout until documented remediation and re-review produce `PASS`.

---

### Change 8

Purpose:

Close the round with evidence-bounded governance addenda and explicit claim boundaries.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase8_closeout/closeout_report.md
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase8_closeout/decisions_addendum.md
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase8_closeout/architecture_addendum.md
Iris/build/description/v2/staging/compose_contract_migration/historical_runtime_vocabulary_readpoint_anchor_round/phase8_closeout/roadmap_addendum.md
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
optional live pointer surfaces selected by placement_disposition_decision.md
```

Implementation Notes:

* Apply governance docs addenda only after hard gates and adversarial review pass.
* Promote the staged central readpoint anchor from Change 5 only in this phase.
* Central anchor and closeout addendum are integrated as one dated readpoint per live governance document, not duplicated as separate entries.
* If option B was selected, promote staged pointer drafts only after the same hard gates and adversarial review pass.
* Append-only addenda must state:

```text
historical active/silent is preserved where it belongs
historical active/silent is not current runtime authority
current runtime authority remains adopted/unadopted
GUARD-A owns current-surface re-entry prevention
anchor is reader-facing governance output and not a machine guard
this round does not claim repo-wide lexical zero, alias removal, runtime rollout, deployment, release readiness, or runtime equivalence
```

* Use this single PASS closeout label:

```text
closed_with_historical_runtime_vocabulary_readpoint_anchor
```

Blocked labels:

```text
blocked_unknown_authority_relevant_active_silent_readpoint
blocked_current_authority_residue_found
blocked_historical_body_mutation_required
blocked_anchor_target_unpatched
blocked_existing_guard_ownership_conflict
```

Validation:

* Addenda are append-only.
* Latest readpoint is clear without rewriting earlier historical entries.
* Gate failure prevents authoritative docs mutation.
* `live_authoritative_doc_written_before_change8 = false`.
* The promoted text matches the staged Change 5 draft except for expected date/path/hash fields recorded in the promotion report.
* Central anchor and closeout addendum are not duplicated as competing entries in the same document.

---

## 7. Validation Plan

### Automated Validation

Required before closeout if implementation creates scanner/validator code or modifies any validation-relevant path:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Required before closeout if Lua/runtime files are touched accidentally or if the round elects to run full invariance smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Required documentation-governance validation:

```text
JSONL parse for occurrence inventory
JSON parse for manifests and reports
authority_relevant_unknown_count = 0
bare_token_sweep_unknown_count = "<actual, non-gate>"
current_authority_forbidden_count = 0
guard_a_escalation_required = false
anchor_required_unpatched_count = 0
hash_sealed_artifact_sha256_unchanged = true
negative invariant report matches expected values
GUARD-A files and ownership unchanged
GUARD-A manifest boundary inherited, not redefined
live_authoritative_doc_written_before_change8 = false
central_anchor_closeout_addendum_integrated = true
git diff review confirms no prohibited mutation
```

If exact commands are not run, closeout must say `not run` or `blocked`, not `passed`.

Validation result recording must use this shape instead of hard-coded historical counts:

```text
python_unittest_command_exited_0 = true
python_unittest_failures = 0
python_unittest_observed_count = "<actual>"
lua_syntax_command_exited_0 = true
lua_syntax_failures = 0
lua_syntax_observed_count = "<actual>"
touched_prohibited_lua_py_fixture_count = 0
```

Path preflight must confirm:

```text
docs/PLAN_TEMPLATE.md exists
docs/Philosophy.md exists
docs/DECISIONS.md exists
docs/ARCHITECTURE.md exists
docs/ROADMAP.md exists
```

### Manual Validation

* Review all anchor text for the Phase 4 contract.
* Review top-doc addenda for latest-readpoint consistency.
* Confirm historical `active` is not described as a live synonym for current `adopted`.
* Confirm diagnostic/import aliases are preserved as non-authority vocabulary.
* Confirm anchor text is reader-facing governance output, not a machine guard.
* Confirm every hash-sealed artifact is protected by wrapper/pointer placement rather than direct edit.
* Confirm no public release, runtime rollout, deployment, or manual in-game QA wording is implied.

### Validation Limits

This execution will not perform:

* runtime validation
* manual in-game QA
* multiplayer validation
* long-session runtime validation
* deployment validation
* Workshop validation
* external mod compatibility sweep
* tooltip completion validation
* runtime equivalence validation
* repo-wide `active/silent` lexical zero validation

---

## 8. Risk Surface Touch

### Authority Surface

None. Current runtime authority remains `adopted/unadopted`. Anchors point to existing authority and do not create a new writer/runtime enum authority.

### Runtime Behavior Surface

None. Runtime Lua, payload writer, packaged Lua, source decisions, rendered text, and consumer behavior are out of scope.

### Compatibility Surface

None. Diagnostic/import/historical alias preservation avoids compatibility changes.

### Sealed Artifact Surface

None mutated. Sealed historical bodies, fixtures, staging artifact bodies, and sha256-referenced artifacts are read and classified but not rewritten. Hash-sealed artifacts must remain byte-identical.

### Public-Facing Output Surface

None. Browser, Wiki, Tooltip, generated reports, packaged Lua, and in-game user-facing surfaces are unchanged.

---

## 9. Risk Analysis

### Architecture Risk

* The anchor could accidentally read as a new authority instead of a pointer to existing `adopted/unadopted` authority.
* The round could blur ownership with GUARD-A by trying to solve current-surface re-entry inside historical anchoring.
* Placement option B could become noisy or be mistaken for historical body mutation unless strictly append-only.
* Placement option B could silently break sha256-referenced artifacts if hash-sealed targets are not excluded before patching.

### Runtime Risk

* Low if scope is followed, because runtime files are immutable.
* Any runtime Lua or packaged Lua diff is a stop-the-line violation and blocks closeout.

### Compatibility Risk

* Low if diagnostic/import aliases are preserved.
* Removing aliases or fixtures would create compatibility and provenance risk; this plan forbids that.

### Regression Risk

* Main regression risk is documentation regression: future readers might infer lexical cleanup, alias deletion, or current enum remigration.
* Occurrence classification omissions could leave a high-value historical surface unanchored.
* Overbroad anchors could imply repo-wide lexical zero or current-surface guard ownership transfer.
* Hash-sealed artifact mutation is a stop-the-line regression even if no existing `active/silent` token changes.

---

## 10. Rollback Plan

All intended changes are additive documentation or round-local staging evidence. If validation fails:

```text
wrong inventory                 -> regenerate inventory before closeout
wrong classification            -> fix classification before anchor draft staging or gated promotion
bad placement disposition        -> revise disposition before patching docs
bad anchor wording               -> remove or revise additive anchor
live doc write attempted early   -> stop-the-line, revert live write, move text back to staged draft, blocked closeout
runtime/source/rendered changed  -> stop-the-line, revert prohibited mutation, blocked closeout
historical body rewritten        -> stop-the-line, revert prohibited mutation, blocked closeout
fixture/staging body rewritten   -> stop-the-line, revert prohibited mutation, blocked closeout
hash-sealed artifact changed     -> stop-the-line, revert byte change, blocked closeout
GUARD-A changed                  -> stop-the-line, revert guard mutation, blocked closeout
```

Round-local staging artifacts may be preserved as failed-run evidence, but must not be read as adopted closeout authority unless the round passes all gates.

---

## 11. Governance Constraints

* `docs/Philosophy.md` is the top authority.
* Hub & Spoke / SPI boundaries remain unaffected; Iris does not alter Pulse Core or another spoke.
* Current canonical runtime authority remains single-writer `adopted/unadopted`.
* Anchors point to authority; they do not create authority.
* Anchors are reader-facing governance output; they are not machine-enforced guards.
* Historical sealed body mutation is forbidden.
* Fixture and staging artifact body token mutation is forbidden.
* Hash-sealed artifact byte mutation is forbidden.
* Diagnostic/import/historical aliases are preserved.
* All anchors are additive.
* Repo-wide lexical zero is forbidden as a success gate.
* GUARD-A owns current-label re-entry prevention and must not be redefined here.
* GUARD-A manifest boundaries are inherited for current-surface tagging and not independently rederived.
* Runtime/build boundary remains intact; runtime Lua is render-only for this round.
* `active/silent` occurrence classification must allow `allowed = true` with `current_authority = false`.
* `authority_relevant_unknown_count = 0` is required before anchor draft staging and closeout.
* Bare-token sweep unknowns are audit evidence, not a lexical-zero gate, unless a specific occurrence is promoted into authority-relevant scope.
* Live authoritative governance docs are mutated only in Change 8 after hard gates and adversarial review pass.
* Closeout claims must be evidence-bounded and must not imply release readiness or deployment.

---

## 12. Expected Closeout State

Expected closeout target:

```text
complete
```

Expected PASS closeout label:

```text
closed_with_historical_runtime_vocabulary_readpoint_anchor
```

Complete means:

```text
active/silent occurrence inventory exists
all occurrences are classified
authority_relevant_unknown_count = 0
bare_token_sweep_unknown_count recorded as non-gate audit evidence
historical/provenance/diagnostic/import/test occurrences are non-current authority
anchor-required historical surfaces are connected to adopted/unadopted current readpoint through staged drafts and gated Change 8 promotion
anchor contract blocks active = live adopted synonym reading
anchor status remains reader-facing governance output, not machine guard
GUARD-A ownership is preserved
hash-sealed artifact sha256 immutability passes
no live authoritative governance doc write occurred before Change 8
central anchor and closeout addendum are integrated as one dated readpoint
negative invariant report passes
adversarial review follows REVIEW_TEMPLATE 1-12 and returns PASS with critical count 0
closeout addenda are append-only and evidence-bounded
```

Blocked closeout states:

```text
blocked_unknown_authority_relevant_active_silent_readpoint
blocked_current_authority_residue_found
blocked_historical_body_mutation_required
blocked_anchor_target_unpatched
blocked_existing_guard_ownership_conflict
```

Expected final claim boundary:

```text
Historical active/silent is preserved where it belongs, but can no longer be read as current runtime authority.
Current runtime authority remains adopted/unadopted.
Sealed historical bodies are not rewritten.
Remaining legacy tokens are classified as historical/provenance/diagnostic/import/test/non-authority vocabulary or escalated to GUARD-A.
This round does not claim repo-wide active/silent zero, alias removal, runtime rollout, deployed closeout, manual in-game QA, Workshop readiness, ready_for_release, or runtime equivalence.
```
