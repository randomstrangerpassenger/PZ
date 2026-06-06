# Iris DVF 3-3 Legacy Active/Silent Current-Surface Guard Round Plan

> 상태: Draft v0.2-plan  
> 기준일: 2026-05-21  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Legacy Active/Silent Current-Surface Guard Round -- ROADMAP (종합본)` (2026-05-21 user-provided synthesis)  
> review input: `Legacy Active/Silent Current-Surface Guard Round -- REVIEW (종합본)` WARN feedback (2026-05-21), R-1 through R-5 incorporated.  
> 근거 결정: `docs/DECISIONS.md` 2026-05-21 `Legacy active/silent current-surface guard is split as follow-up hardening`  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`; the template is a project planning form under `docs/`, not semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`.  
> 실행 상태: planning authority only. 이 문서는 guard/hardening round를 열기 위한 실행 계획이며, 작성 시점에는 runtime Lua, generated runtime artifacts, rendered text, source decisions, deployed state, release state, top-doc closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 legacy `active / silent`가 current Iris authority path에서 current runtime-state label 또는 generated report/operator label로 재유입되는 것을 막는 build-time guard round의 실행 범위와 검증 계약을 고정하는 것이다.

핵심 objective:

```text
future current-surface active/silent current-label reentry must fail loud
historical/diagnostic/import/metric/test usage must remain explicitly allowed
repo-wide lexical zero is not a success criterion
original generated report/operator artifact cleanup success is not claimed
```

이번 round는 `Static Report Label Cleanup Referent Recovery Round` Branch D `blocked_missing_original_operator_artifact_referent` 이후의 후속 hardening이다. 과거 generated report/operator artifact referent를 복구하거나 cleanup 성공을 선언하는 round가 아니라, current authority path에 대한 hard-fail surface와 allow surface를 manifest로 분리하고 validator/test로 fail-loud 경계를 설치하는 round다.

Expected closeout targets:

```text
GUARD-A -- closed_with_no_current_surface_residue_found_and_guarded
GUARD-B -- closed_with_current_surface_residue_rewritten_and_guarded
```

Blocked closeout targets:

```text
GUARD-C -- blocked_unclassified_legacy_active_silent_occurrence
GUARD-D -- blocked_guard_manifest_too_broad_or_unstable
```

Rejected closeout wording:

```text
original_artifact_cleanup_success
repo_wide_active_silent_zero
diagnostic_alias_removed
runtime_deployed
manual_in_game_qa_passed
workshop_ready
ready_for_release
```

---

## 2. Scope

This round is a build-time guard, inventory, and evidence-bounded closeout round. It is not a runtime behavior round, release readiness round, or historical cleanup round.

In scope:

* Scope lock and authority readpoint seal for `Legacy Active/Silent Current-Surface Guard Round`.
* New round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/
```

* New current-surface guard referent manifest:

```text
phase1_manifest/current_surface_guard_referent_manifest.json
```

* Manifest-defined hard-fail surfaces:

```text
current runtime payload
current writer output
current generated report / operator output
packaged Lua data
```

The hard-fail surface set is intentionally limited to the four sealed surfaces above. `current generated report / operator output` includes current build-produced operator reports, but excludes validator/scanner diagnostic output and round-local staging evidence.

* Manifest-defined allow surfaces:

```text
historical sealed body
staging evidence
round-local scanner / validator diagnostic output
validator error catalog
negative fixture / expected-failure payload
diagnostic-only artifact
import alias
legacy metric key
explicit legacy test fixture
non-label lexical/code identifier occurrence
```

* Manifest classification precedence:

```text
1. Round-local staging evidence wins over generic build/report path matching.
2. Hard-fail requires both a sealed hard-fail surface and a current-label occurrence.
3. A current-label occurrence is one of runtime_state_value, source_value, operator_label_value,
   current_report_label_value, or writer_output_label_value with current_label_candidate = true.
4. occurrence_kind in diagnostic_alias, legacy_metric_key, plain_text, code_identifier,
   historical_quote, or explicit_legacy_test_fixture is allowed only when a matching allow rule
   exists and must_not_be_current_output is satisfied.
5. No allow rule may downgrade an occurrence that is actually rendering or serializing a current
   runtime/operator state label.
```

* Occurrence inventory for `active / silent` with occurrence kind, surface class, allow rule, current-label candidacy, and disposition.
* Conditional GUARD-B rewrite only if hard-fail current-label residue is found.
* Build-time validator:

```text
Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py
```

* Guard tests:

```text
Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py
```

* Fail-loud error catalog:

```text
CURRENT_SURFACE_REJECTED_LEGACY_ACTIVE_SILENT_LABEL
UNALLOWLISTED_LEGACY_ACTIVE_SILENT_OCCURRENCE
ALLOWLIST_RULE_TOO_BROAD
DIAGNOSTIC_ALIAS_USED_OUTSIDE_EXPLICIT_DIAGNOSTIC_SURFACE
LEGACY_METRIC_KEY_RENDERED_AS_CURRENT_LABEL
```

* Dual independent gates:

```text
Gate A = allowlist 밖 current-label occurrence 0
Gate B = negative fixture hard-fail reach verified
```

* Evidence-bounded closeout and top-doc addendum drafts after gates pass.

### Explicitly Out Of Scope

* Original generated report/operator artifact referent recovery.
* Reopening `Static Report Label Cleanup Referent Recovery Round`.
* Repo-wide `active / silent` lexical zero.
* Diagnostic/import/historical alias removal.
* Historical body rewrite in `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, walkthroughs, or archived closeouts.
* Legacy metric key removal unless it is rendered as a current label.
* `runtime_state` vocabulary redesign beyond the already sealed `adopted / unadopted` canonical enum.
* `quality_state` or `publish_state` redesign.
* Current 2105 row identity rebaseline.
* Rendered text regeneration.
* Runtime Lua guard logic.
* Runtime rollout, deployed closeout, manual in-game QA, Workshop readiness, or `ready_for_release`.

---

## 3. Non-Goals

* Prove the original Static Report Label Cleanup artifact cleanup succeeded.
* Convert every `active / silent` token in the repository.
* Delete diagnostic/import/historical compatibility aliases.
* Delete legacy metric keys such as `active_count` and `silent_count`.
* Treat `activeView`, `isActive`, `silent failure`, historical closeout text, or legacy worksheet text as residue by lexical match alone.
* Promote validator/linter/bridge/runtime consumer into writer authority.
* Put current-label adjudication logic into runtime Lua.
* Use Python/Lua validation pass as evidence of deployed runtime behavior.
* Claim release eligibility or public rollout readiness.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` remains the top authority.
* `docs/DECISIONS.md` 2026-05-21 redefines this issue as follow-up hardening, not past artifact cleanup.
* `docs/ARCHITECTURE.md` current readpoint states that legacy `active / silent` future reentry prevention is a separate guard/hardening axis.
* `docs/ROADMAP.md` `Next` requires the guard round to begin with a current-surface guard referent manifest.

Runtime/state assumptions:

* Current runtime payload canonical enum is `adopted / unadopted`.
* Legacy `active / silent` is allowed only as diagnostic/import/historical read-only alias or explicitly allowed legacy evidence.
* Current 2105 baseline remains `adopted 2084 / unadopted 21`.
* Runtime chunk `source = "unadopted"` is already sealed by the Runtime Payload Enum Rename Scope Round.
* `runtime_state`, `quality_state`, and `publish_state` remain separate axes.

Implementation assumptions:

* Compose writer remains the single writer for canonical current output.
* The round-local builder is the only writer for round-local staging artifacts:

```text
Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py
```

* Validator, tests, scanner, linter, bridge, and runtime consumers are not writer authority.
* Guard logic belongs to offline Python build/validation lanes, not runtime Lua.
* Existing guards remain authoritative and must not be weakened:

```text
DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM
DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL
```

Validation assumptions:

* Prior baseline was Python unittest discovery passing and Lua syntax passing; this round must record observed test/file counts and must not claim pass unless the exact relevant commands exit code `0`.
* Python tests and Lua syntax validation are implementation/static-validation evidence only.

---

## 5. Repository Areas Affected

### Code

* `Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py`
* `Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py`
* `Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py`
* Existing build/test entrypoint files only if needed to connect the validator to the default build/test path.
* Conditional GUARD-B only: writer files that actually emit confirmed hard-fail current-label residue.

### Docs

* `docs/Iris/iris-dvf-3-3-legacy-active-silent-current-surface-guard-round-plan.md`
* Conditional closeout addenda drafts for:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Top-doc addenda are allowed only after the relevant gates pass or a blocked closeout is explicitly recorded. Historical decision bodies must not be rewritten.

### Config

* None planned.
* If validator wiring requires a local test/build config change, the change must be listed in the phase report before implementation.

### Generated Artifacts

Primary round-local artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/
```

Planned phase artifacts:

```text
phase0_scope_lock/scope_lock.md
phase0_scope_lock/prior_readpoint_summary.json
phase1_manifest/current_surface_guard_referent_manifest.json
phase1_manifest/hard_fail_surface_manifest.json
phase1_manifest/allow_surface_manifest.json
phase1_manifest/baseline_seal_report.json
phase2_inventory/legacy_active_silent_occurrence_inventory.jsonl
phase2_inventory/current_label_candidate_inventory.json
phase2_inventory/allowed_occurrence_inventory.json
phase2_inventory/unclassified_occurrence_inventory.json
phase3_adjudication/occurrence_adjudication_report.json
phase3_adjudication/branch_decision.json
phase4_mutation_if_needed/phase3_execution_diff_report.json
phase5_guard/current_surface_guard_report.json
phase5_guard/validator_error_catalog.json
phase5_negative_invariant_report.json
phase6_validation/python_unittest_report.txt
phase6_validation/lua_syntax_report.txt
phase6_validation/static_dynamic_residue_report.json
phase6_validation/phase6_hard_gate_report.json
phase7_adversarial_review.md
phase7_closeout/closeout.json
phase7_closeout/closeout.md
```

Conditional GUARD-B generated/runtime artifacts may be touched only if the phase inventory proves a hard-fail current-label residue and the origin is artifact-only or writer-backed with clear regeneration/rewrite evidence.

---

## 6. Planned Changes

### Change 1

Purpose:

Seal scope, authority readpoints, forbidden mutations, and the working definition of a current-label occurrence.

Files:

```text
Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase0_scope_lock/scope_lock.md
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase0_scope_lock/prior_readpoint_summary.json
```

Implementation Notes:

* Record the Runtime Payload Enum Rename Scope Round, Static Report Label Cleanup Round, Static Report Label Cleanup Referent Recovery Branch D, and 2026-05-21 guard split decision.
* Explicitly state that this is not original artifact cleanup success, referent recovery reopen, repo-wide zero, alias removal, runtime rollout, or `ready_for_release`.
* Define `current label occurrence` as a value or rendered label position that presents `active / silent` as current runtime/operator state rather than historical, diagnostic, metric, fixture, identifier, or plain text.

Validation:

* Scope lock contains all non-decision statements required by this plan.
* Scope lock names the authority documents and relevant readpoints.

---

### Change 2

Purpose:

Create the current-surface guard referent manifest and split hard-fail surfaces from allow surfaces.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase1_manifest/current_surface_guard_referent_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase1_manifest/hard_fail_surface_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase1_manifest/allow_surface_manifest.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase1_manifest/baseline_seal_report.json
```

Implementation Notes:

* Allow rules must be structured as `path_glob + occurrence_kind + reason + must_not_be_current_output`.
* Broad path-only allow rules are invalid.
* Required hard-fail surfaces are limited to current runtime payload, current writer output, current generated report/operator output, and packaged Lua data.
* Required allow surfaces include historical sealed body, staging evidence, round-local scanner/validator diagnostic output, validator error catalog, negative fixtures, expected-failure payloads, diagnostic-only artifact, import alias, legacy metric key, explicit legacy test fixture, and non-label lexical/code identifier occurrence.
* The manifest must document classification precedence:

```text
surface membership nominates a candidate surface
occurrence_kind + current_label_candidate decide disposition
round-local staging evidence is allow, never hard-fail by generic build/report path matching
```

* The manifest must document its boundary with `DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM` and `DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL`.
* Primary error ownership must be single-owner by surface:

```text
runtime_state writer/validator occurrence -> DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM
legacy resolver compatibility label occurrence -> DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL
packaged Lua data / generated report-operator output / current writer non-runtime label -> CURRENT_SURFACE_REJECTED_LEGACY_ACTIVE_SILENT_LABEL
```

If an occurrence could match both old and new guards, the existing guard owns the primary error and the new guard records or tests it as `covered_by_existing_guard` without emitting a duplicate primary failure.

Validation:

* Manifest schema validation passes.
* Every allow rule has reason, occurrence kind, and `must_not_be_current_output = true` where applicable.
* Meta-rule rejects allowlist patterns that cover current output without explicit occurrence constraints.
* A fixture proves round-local scanner/validator output containing literal `active / silent` tokens is allowed as diagnostic staging evidence and does not trip Gate A.

---

### Change 3

Purpose:

Inventory and classify all relevant `active / silent` occurrences without mutation-first cleanup.

Files:

```text
Iris/build/description/v2/tools/build/build_legacy_active_silent_current_surface_guard_round.py
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase2_inventory/legacy_active_silent_occurrence_inventory.jsonl
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase2_inventory/current_label_candidate_inventory.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase2_inventory/allowed_occurrence_inventory.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase2_inventory/unclassified_occurrence_inventory.json
```

Implementation Notes:

* Scan JSON, JSONL, Lua, Markdown, Python, and current generated output surfaces relevant to the manifest.
* Record at minimum:

```json
{
  "path": "string",
  "line": 0,
  "column": 0,
  "token": "active|silent",
  "nearby_key": "runtime_state|state|source|label|operator_label|null",
  "occurrence_kind": "runtime_state_value|source_value|operator_label_value|current_report_label_value|writer_output_label_value|historical_quote|diagnostic_alias|legacy_metric_key|code_identifier|plain_text|explicit_legacy_test_fixture",
  "surface_class": "hard_fail|allow|unclassified",
  "allow_rule_id": "string|null",
  "current_label_candidate": true,
  "disposition": "rewrite_required|allowed|ignore_non_label|blocked_unclassified"
}
```

* Separate four inventories: hard-fail residue, allowed occurrence, non-label lexical occurrence, and unclassified blocker.
* `activeView`, `isActive`, and `silent failure` must not be treated as current-label residue by lexical match alone.

Validation:

* Scanner output is deterministic across repeated runs.
* Unclassified inventory is empty for GUARD-A/GUARD-B, or GUARD-C is selected without mutation.
* Hard-fail current-label candidates and allowed occurrences are separated.

---

### Change 4

Purpose:

Adjudicate occurrence disposition and select GUARD-A/GUARD-B/GUARD-C/GUARD-D.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase3_adjudication/occurrence_adjudication_report.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase3_adjudication/branch_decision.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase4_mutation_if_needed/phase3_execution_diff_report.json
```

Implementation Notes:

* GUARD-A requires hard-fail residue `0`, unclassified `0`, and guard/test completion.
* GUARD-B requires confirmed hard-fail residue, rewrite/regeneration to `0`, and guard/test completion.
* GUARD-C blocks if an occurrence cannot be classified as current label or allowed usage.
* GUARD-D blocks if manifest allow rules are too broad or unstable.
* GUARD-C/GUARD-D must perform no mutation.
* GUARD-B rewrite mapping:

```text
runtime_state: active  -> runtime_state: adopted
runtime_state: silent  -> runtime_state: unadopted
source: silent         -> source: unadopted
operator label active  -> adopted
operator label silent  -> unadopted
```

* Legacy metric keys are retained unless they are rendered as current labels. If needed, add current counts beside legacy keys rather than deleting compatibility metrics:

```json
{
  "legacy_metric_keys": { "active_count": 2084, "silent_count": 21 },
  "current_runtime_state_counts": { "adopted": 2084, "unadopted": 21 }
}
```

Validation:

* Branch decision records evidence and pre/post residue counts.
* Immutable surface hashes remain unchanged.
* Writer-origin residue is fixed at writer origin, not artifact-only patch.
* Artifact-only residue has explicit stale-artifact disposition evidence.

---

### Change 5

Purpose:

Install fail-loud validator and tests for future current-surface reentry.

Files:

```text
Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py
Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase5_guard/current_surface_guard_report.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase5_guard/validator_error_catalog.json
```

Implementation Notes:

* Negative fixtures must fail with expected error codes:

```text
runtime payload "runtime_state": "active" -> DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM
Lua chunk source = "silent" -> CURRENT_SURFACE_REJECTED_LEGACY_ACTIVE_SILENT_LABEL
generated operator report active rows as current label -> CURRENT_SURFACE_REJECTED_LEGACY_ACTIVE_SILENT_LABEL
writer output label silent -> CURRENT_SURFACE_REJECTED_LEGACY_ACTIVE_SILENT_LABEL
```

* Positive fixtures must pass:

```text
historical closeout body
diagnostic/import alias fixture
legacy metric key retained but not rendered as current label
activeView, isActive, silent failure
round-local scanner/validator inventory or error catalog containing active/silent as diagnostic evidence
```

* Include a too-broad allowlist test.
* Compose with existing `DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM` behavior without weakening or replacing it.
* Runtime-state writer/validator occurrences use `DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM` as the primary owner. The new manifest guard owns packaged Lua data, generated report/operator output, and current writer non-runtime label surfaces.

Validation:

* Negative fixtures fail loud with the expected error code.
* Positive fixtures pass.
* Existing guard behavior remains unchanged.
* Duplicate primary error emission is rejected by tests.

---

### Change 6

Purpose:

Verify negative invariants and prove allow surfaces were not mutated.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase5_negative_invariant_report.json
```

Implementation Notes:

* Hash-check historical sealed body, staging evidence, diagnostic/import alias, legacy metric key, and explicit test fixture surfaces.
* Verify rendered text, chunk topology, runtime_state, quality_state, and publish_state invariants.
* Verify existing guard error behavior remains stable.

Validation:

* All protected surfaces remain unchanged unless GUARD-B explicitly permits a current hard-fail artifact or writer surface change.
* Runtime/build-time separation remains intact.

---

### Change 7

Purpose:

Run static and dynamic validation as independent dual gates.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase6_validation/python_unittest_report.txt
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase6_validation/lua_syntax_report.txt
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase6_validation/static_dynamic_residue_report.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase6_validation/phase6_hard_gate_report.json
```

Implementation Notes:

* Gate A and Gate B must remain independent:

```text
Gate A: allowlist 밖 current-label occurrence 0 after final scan; if GUARD-B rewrites residue, this is the post-rewrite rescan
Gate B: four negative hard-fail surfaces actually fail loud
```

* Run the standalone validator using the manifest and repo root.
* Run Python unittest discovery and Lua syntax check.
* Record default build/test path wiring proof in the Phase 6 hard gate. This is a hard-gate prerequisite, not a third residue gate.

Validation:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

```powershell
python -B Iris\build\description\v2\tools\validate_legacy_active_silent_current_surface_guard.py `
  --manifest Iris\build\description\v2\staging\compose_contract_migration\legacy_active_silent_current_surface_guard_round\phase1_manifest\current_surface_guard_referent_manifest.json `
  --repo-root .
```

Expected pass wording if and only if commands exit `0`:

```text
Python unittest discovery / OK with observed test count recorded
Lua syntax / OK with observed Lua file count recorded
validator standalone / OK
```

---

### Change 8

Purpose:

Perform adversarial review against sealed decisions and claim boundaries.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase7_adversarial_review.md
```

Implementation Notes:

* Use `docs/REVIEW_TEMPLATE.md` structure:

```text
Good Points
Critical
Important
Minor
Verdict
```

* Review for broad allowlist, false-positive/false-negative risk, historical mutation risk, writer/artifact mismatch, existing guard conflict, and release claim overreach.

Validation:

* Critical blockers must be `0` for GUARD-A/GUARD-B closeout.
* If blockers remain, close as GUARD-C/GUARD-D or equivalent blocked state.

---

### Change 9

Purpose:

Write evidence-bounded closeout and addendum drafts.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase7_closeout/closeout.json
Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase7_closeout/closeout.md
```

Conditional docs after gates pass or blocked closeout is recorded:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Implementation Notes:

* Closeout must record branch result, mutation status, residue counts, guard/test status, invariant status, and validation command results.
* No-residue closeout must emphasize that the round added a guard; it must not claim cleanup success.
* Suggested addendum claim:

```text
Legacy active/silent current-surface guard는 과거 generated report/operator artifact cleanup success가 아니라 future current-surface 재유입 방지 hardening으로 닫는다.
```

Validation:

* Closeout explicitly states the non-decisions:

```text
original artifact cleanup success 아님
repo-wide zero 아님
alias removal 아님
runtime rollout 아님
deployed closeout 아님
manual in-game QA pass 아님
Workshop readiness 아님
ready_for_release 아님
```

---

## 7. Validation Plan

### Automated Validation

Required validation commands:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

```powershell
python -B Iris\build\description\v2\tools\validate_legacy_active_silent_current_surface_guard.py `
  --manifest Iris\build\description\v2\staging\compose_contract_migration\legacy_active_silent_current_surface_guard_round\phase1_manifest\current_surface_guard_referent_manifest.json `
  --repo-root .
```

Required automated checks:

* Manifest schema validation.
* Allowlist broadness rejection test.
* Deterministic scanner rerun check.
* Static residue Gate A: allowlist outside current-label occurrence `0` after final scan; for GUARD-B, this means post-rewrite rescan.
* Guard reach Gate B: four negative fixtures fail-loud.
* Positive fixture pass checks for historical/diagnostic/import/metric/test/non-label usage and round-local diagnostic self-output.
* Existing guard compatibility checks for `DEFAULT_RUNTIME_STATE_REJECTED_LEGACY_ENUM` and `DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL`.
* Single-owner error precedence check for duplicate old/new guard matches.
* Default build/test path wiring proof.
* Immutable surface hash checks.
* Rendered text, chunk topology, `runtime_state`, `quality_state`, and `publish_state` invariance checks.

### Manual Validation

Manual validation is limited to review/inspection of generated phase reports and the adversarial review.

No manual in-game QA is part of this plan.

### Validation Limits

This plan will not perform:

* Runtime rollout validation.
* Deployed mod validation.
* Manual in-game QA.
* Workshop release validation.
* External mod compatibility sweep.
* Long-session runtime validation.
* Full release checklist validation.
* Original artifact referent recovery beyond the already closed Branch D decision.

---

## 8. Risk Surface Touch

### Authority Surface

Touched. The round adds a new guard referent manifest and closeout evidence. It must preserve the sealed canonical enum `adopted / unadopted` and must not reopen historical cleanup decisions.

### Runtime Behavior Surface

None planned. Validator logic is offline Python build/validation logic. Runtime Lua must remain render-only and must not receive current-label adjudication logic.

### Compatibility Surface

Touched only at diagnostic/import/metric/test boundaries. Diagnostic/import aliases and legacy metric keys are preserved unless they are rendered as current labels.

### Sealed Artifact Surface

Read-only except for explicitly permitted GUARD-B hard-fail current surface changes. Historical sealed bodies, staging evidence, and archived closeouts must remain unchanged.

### Public-Facing Output Surface

Potentially touched only if a confirmed current generated report/operator output contains hard-fail legacy current labels. Public release claims remain out of scope.

---

## 9. Risk Analysis

### Architecture Risk

* A too-broad allowlist can nullify the guard by allowing current output residue.
* A too-narrow hard-fail classification can turn historical or diagnostic evidence into false positives.
* Treating validator/test code as writer authority would violate the single-writer model.
* Reopening past cleanup recovery would blur the Static Report Label Cleanup Referent Recovery Branch D terminal decision.

### Runtime Risk

* Runtime risk is low if guard logic stays offline.
* Runtime risk increases if Lua consumer code is modified to adjudicate labels.
* GUARD-B runtime artifact rewrites can accidentally affect chunk topology or rendered text if not hash-checked.

### Compatibility Risk

* Removing legacy metric keys can break downstream compatibility.
* Removing diagnostic/import alias handling can break explicit diagnostic or import paths.
* Existing fail-loud guards may conflict if duplicate error paths are not composed cleanly.

### Regression Risk

* Artifact-only patching can regress on next generation if the writer is the true source.
* Lexical grep-style scanning can miss structured values or over-report identifiers.
* Generated report/operator fixtures may be insufficient unless negative reach tests cover all four sealed hard-fail surfaces.
* Validation can pass without being wired into the default build/test path unless wiring is explicitly checked.

---

## 10. Rollback Plan

Rollback is scoped by change type:

* Manifest rollback: revert `phase1_manifest/*` and adjust overly broad or unstable rules before reopening validation.
* Scanner/validator rollback: revert validator and test files. If this happens, GUARD-A/GUARD-B closeout is impossible and the round must close as blocked.
* Writer mutation rollback: revert writer changes and associated generated artifact rewrites together. If residue remains, GUARD-B closeout is forbidden.
* Artifact-only rollback: revert stale generated output changes and re-adjudicate whether the residue is writer-origin or artifact-only.
* Documentation rollback: prefer a superseding addendum over historical body rewrite. Do not rewrite sealed historical decision bodies.

If Phase 3 performs no mutation, rollback is limited to deleting or reverting round-local staging artifacts and the new validator/test files. A no-residue closeout without guard/test remains invalid.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris remains a wiki-style information module: no interpretation, recommendation, comparison, or user-facing judgment is introduced.
* `active / silent` must not be restored as current canonical labels.
* Repo-wide lexical zero is forbidden as a goal.
* Historical body direct rewrite is forbidden.
* Diagnostic/import aliases are preserved.
* Mutation-first cleanup is forbidden.
* Single-writer authority is preserved.
* Runtime/build-time separation is preserved.
* Runtime Lua remains render-only.
* Existing fail-loud guards must not be weakened or bypassed.
* Static residue count and guard reach are independent gates.
* Passing Python tests or Lua syntax does not imply runtime rollout, deployed closeout, manual in-game QA, Workshop readiness, or `ready_for_release`.
* Dirty working tree handling must preserve unrelated user changes.

---

## 12. Expected Closeout State

Expected successful closeout:

```text
GUARD-A -- closed_with_no_current_surface_residue_found_and_guarded
```

or:

```text
GUARD-B -- closed_with_current_surface_residue_rewritten_and_guarded
```

GUARD-A requires:

* `current_surface_guard_referent_manifest.json` exists.
* Hard-fail and allow surfaces are manifest-separated.
* Occurrence inventory is deterministic.
* Allowlist outside current-label occurrence count is `0` after final scan.
* Unclassified occurrence count is `0`.
* Validator/test fail-loud guard is installed.
* Gate A and Gate B both pass independently.
* Historical/diagnostic/import/metric/test usage remains unmutated.

GUARD-B requires all GUARD-A guard conditions plus:

* Pre-rewrite hard-fail residue is recorded.
* Writer-origin residue is fixed at writer origin, or artifact-only residue is justified.
* Post-rewrite hard-fail residue is `0`.
* Invariant report proves no forbidden surface changed.

Blocked closeout:

```text
GUARD-C -- blocked_unclassified_legacy_active_silent_occurrence
GUARD-D -- blocked_guard_manifest_too_broad_or_unstable
```

If the expected closeout is not `complete`, the reason must be explicit:

* unclassified occurrence exists,
* allowlist is too broad or unstable,
* negative guard reach fails,
* immutable surface hash changed,
* validation tool is unavailable,
* or default build/test wiring is not proven.

No closeout may claim:

```text
original artifact cleanup success
repo-wide active/silent zero
diagnostic/import/historical alias removal
runtime rollout
deployed closeout
manual in-game QA pass
Workshop readiness
ready_for_release
```
