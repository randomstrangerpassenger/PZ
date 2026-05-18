# Iris DVF 3-3 Adapter / Diagnostic Compatibility Final Disposition Round Plan

> 상태: Draft v0.1-plan  
> 기준일: 2026-05-18  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Adapter / Diagnostic Compatibility Final Disposition Round - Synthesized Roadmap` (2026-05-18 user-provided synthesis)  
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`.  
> 실행 상태: planning authority only. 이 문서는 final disposition round를 열기 위한 실행 계획이며, 작성 시점에는 resolver code, runtime Lua, generated runtime artifacts, rendered text, quality/publish state, deployed state, top-doc closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 `Diagnostic-only Resolver Compatibility Guard Round` 이후 남은 두 잔여 표면을 correctness debt가 아니라 disposition debt로 처리하고, `Resolver Compatibility / Adapter Cleanup` category를 evidence-bounded closeout으로 닫기 위한 실행 계약을 고정하는 것이다.

채택된 disposition option:

```text
Option C
  legacy compatibility mapping: preserve
  adapter surface: remove, conditional on dynamic reach probe PASS
```

Expected closeout target on probe PASS:

```text
closed_with_adapter_removed_mapping_permanently_diagnostic_only
```

Fallback closeout target on probe FAIL:

```text
closed_with_adapter_preserved_mapping_permanently_diagnostic_only
```

This probe FAIL branch is an accepted fallback retained-adapter disposition, not an Option C success. Option C success requires mapping preservation and adapter removal.

Probe PASS closeout wording ceiling:

```text
Adapter / Diagnostic Compatibility Final Disposition Round closes Option C.

- legacy compatibility mapping is permanently retained as a diagnostic-only non-authority fixture.
- adapter surface is removed as a post-migration transitional compatibility surface.
- selected_role / selected_role_precedence / selected_role_target remain untouched native resolver authority / trace.
- No runtime Lua regeneration.
- No deployed closeout.
- No ready_for_release claim.
```

Round naming alignment:

```text
Sealed #43 named the possible follow-up as Adapter / Diagnostic Compatibility Disposition Round.
This plan intentionally adopts Adapter / Diagnostic Compatibility Final Disposition Round because it is scoped to dispose of both residual surfaces identified by #43, not to reopen active resolver correctness debt.
The "Final" label is valid only within the bounded residual disposition category and does not block future reopening under the explicit reopen triggers in Phase 9.
```

---

## 2. Scope

This round is a build-time resolver/adapter disposition round. It is not a runtime rollout, release readiness, complete-removal cleanup, or selected-role redesign round.

In scope:

* Baseline sealing for current resolver, rendered, Lua bridge, selected-role, and test-count invariants.
* Static surface mapping for:
  * adapter implementation files
  * adapter imports and callsites
  * adapter tests and fixtures
  * adapter documentation references
  * legacy compatibility mapping module, import graph, diagnostic reach path, and guard tests
* Dynamic reach probing for adapter dependency across the integrated facts input.
* Conditional adapter physical removal when dynamic reach count is `0`.
* Fallback branch sealing when adapter dynamic dependency is non-zero.
* Permanent diagnostic-only seal for legacy compatibility mapping.
* Static and dynamic isolation audits proving mapping is non-default, non-authority, and non-writer.
* Selected-role negative invariant verification before and after adapter disposition.
* Diagnostic/audit loss assessment after adapter removal or preservation.
* Hard gate verification:
  * rendered delta `0`
  * Lua/runtime unchanged
  * no runtime Lua regeneration
  * adapter default/writer dependency `0`
  * default legacy fallback reach `0`
  * selected-role influence unchanged
  * full unittest suite OK, with guard-round invariant coverage preserved
* Adversarial review of phase artifacts.
* Documentation closeout entries in `DECISIONS.md`, `ROADMAP.md`, and `ARCHITECTURE.md` after successful execution.
* Final closeout packet with manifest, touched surface list, validation summary, mutation/no-change disclosure, and claim boundary.

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/adapter_diagnostic_compatibility_final_disposition_round/
```

Recommended phase directories:

```text
phase1_baseline/
phase2_adapter_probe/
phase3_adapter_removal/
phase4_mapping_seal/
phase5_selected_role_invariant/
phase6_diagnostic_audit_check/
phase7_hard_gate/
phase8_review/
phase9_documentation/
phase10_closeout/
```

### Explicitly Out Of Scope

* `selected_role` removal.
* `selected_role_precedence` removal.
* `selected_role_target` removal.
* selected-role influence `0` as a completion condition.
* selected-role architectural redesign.
* complete-removal cleanup reopening.
* Frozen 2105 baseline reconstruction.
* AI-trace authority rebaseline.
* Body plan compose authority redesign.
* Default resolver behavior change beyond adapter removal and retained diagnostic boundary validation.
* Namespace contract mutation.
* Legacy compatibility mapping physical deletion.
* Adapter preservation branch adoption when Phase 2 probe PASSes.
* Removing every historical artifact, test fixture, staging trace, or document mention that contains the word adapter.
* Runtime Lua artifact regeneration.
* Manual in-game QA pass.
* Deployed closeout.
* Workshop release readiness.
* `ready_for_release` declaration.
* Full runtime equivalence claim.
* Full external compatibility preservation claim.

---

## 3. Non-Goals

This plan does not attempt to:

* Reopen sealed decisions #41, #42, or #43.
* Amend the 2026-05-17 selected-role native authority decision.
* Treat `selected_role`, `selected_role_precedence`, or `selected_role_target` as legacy residue.
* Remove the legacy compatibility mapping merely because it exists.
* Make retained legacy mapping a default fallback or writer dependency.
* Convert diagnostic resolver mode into a general compatibility execution path.
* Change current default compose authority.
* Change native `body_plan` path semantics.
* Change facts-layer content or repair downstream facts.
* Use static residue count alone as closeout evidence.
* Use dynamic reach count alone as closeout evidence.
* Declare the adapter removed because `default_adapter_dependency_count = 0`; that value remains a derived alias of `default_path_legacy_fallback_reach_count`.
* Mutate `quality_state`, `publish_state`, rendered descriptions, or public-facing runtime output.
* Claim deployed/runtime QA readiness from a build-time no-delta gate.

---

## 4. Assumptions

Authority assumptions:

* `docs/Philosophy.md` is the top authority.
* Hub & Spoke / SPI boundaries remain mandatory.
* Iris remains a 100% Lua runtime module; this round is build-time tooling and docs only unless code removal affects build-time resolver/adapter Python surfaces.
* Current default compose authority remains `compose_profiles_v2.json + body_plan`.
* `selected_role`, `selected_role_precedence`, and `selected_role_target` are native resolver authority / trace, not cleanup targets.
* Legacy compatibility mapping is already blocked from silent default authority by `DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL`.
* Explicit diagnostic resolver mode remains guarded by diagnostic output-root constraints.

Baseline assumptions at round entry:

```text
legacy_fallback_target_count = 0
default_path_legacy_fallback_reach_count = 0
default_adapter_dependency_count = 0
selected_role_target_legacy_authority_count = 0
selected_role_target_masked_legacy_fallback_reach_count = 0
adapter non-writer boundary = maintained
latest guard-round full validation = 386 tests / OK
Lua/runtime = unchanged
```

Evidence assumptions:

* Static residue and dynamic execution reach are independent gates.
* The selected-role bridge pattern showed that static zero can coexist with non-zero dynamic influence; this round must seal both dimensions.
* Adapter removal proceeds only if Phase 2 dynamic reach probe confirms zero dynamic dependency for default and writer paths.
* Mapping preservation is intentional and must be reframed as a diagnostic-only non-authority fixture, not unfinished cleanup.

---

## 5. Repository Areas Affected

### Code

Expected only if Phase 2 probe PASSes:

* Adapter implementation files discovered in Phase 1 surface map.
* Adapter imports, registrations, aliases, facades, and callsites discovered in Phase 1 surface map.
* Adapter-specific tests that must be removed or converted to native path tests.
* Diagnostic resolver tests or invariant tests needed to prove retained mapping isolation.

Explicitly protected:

* Runtime Lua files.
* Generated deployable Lua chunk files and manifests.
* `selected_role`, `selected_role_precedence`, `selected_role_target` native resolver behavior and trace semantics.
* Facts-layer inputs.

### Docs

Planned execution docs to update only in Phase 9 after gates pass:

* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* `docs/ARCHITECTURE.md`

Planned round artifacts:

* `Iris/build/description/v2/staging/compose_contract_migration/adapter_diagnostic_compatibility_final_disposition_round/**`

This planning document:

* `docs/Iris/Done/plan/iris-dvf-3-3-adapter-diagnostic-compatibility-final-disposition-round-plan.md`

### Config

None expected. If validation discovers a required config touch, the execution must record it in the touched surface manifest and prove it does not alter runtime/deployed state.

### Generated Artifacts

Allowed generated artifacts are diagnostic/audit/round artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/adapter_diagnostic_compatibility_final_disposition_round/
```

Forbidden generated artifacts:

* runtime Lua regeneration
* deployed Lua chunk regeneration
* rendered runtime artifact rebaseline
* quality/publish state generated mutation

---

## 6. Planned Changes

### Change 1

Purpose:

Seal Phase 1 baseline and map adapter/mapping surfaces before any mutation.

Files:

* `phase1_baseline/baseline_snapshot.json`
* `phase1_baseline/adapter_surface_map.json`
* `phase1_baseline/mapping_surface_map.json`
* `phase1_baseline/scope_lock_option_c_seal.md`

Implementation Notes:

* Record baseline test count, rendered hash, Lua bridge hash, AI-trace selected-role dependency counts, default fallback counts, and adapter dependency aliases.
* Map adapter surface by file, module, import site, callsite, tests, fixtures, docs references, and staging traces.
* Map legacy compatibility mapping location, owner, diagnostic reach path, fail-loud guard relationship, and writer/default disconnection.
* Seal official round name:

```text
Adapter / Diagnostic Compatibility Final Disposition Round
```

* Seal selected option:

```text
Option C = Mapping preserved / Adapter removed
```

Validation:

* Baseline hash records are internally consistent.
* Surface maps cover static grep and import/call graph findings.
* Scope lock explicitly lists selected-role untouched, mapping deletion non-goal, runtime Lua regeneration non-goal, and `ready_for_release` non-goal.

---

### Change 2

Purpose:

Run Phase 2 adapter dynamic reach probe and seal the removal/preservation branch before editing adapter code.

Files:

* `phase2_adapter_probe/dynamic_reach_probe_result.json`
* `phase2_adapter_probe/probe_disposition_decision.json`

Implementation Notes:

Measure:

```text
adapter_file_count
adapter_import_count
adapter_callsite_count
adapter_default_dependency_count
adapter_writer_dependency_count
adapter_diagnostic_dependency_count
adapter_test_fixture_dependency_count
adapter_docs_reference_count
adapter_dynamic_reach_count
```

Branch rule:

```text
if adapter_dynamic_reach_count == 0 and adapter_default_dependency_count == 0 and adapter_writer_dependency_count == 0:
  Phase 3 adapter removal may proceed
else:
  Phase 3 is skipped
  closeout branch becomes fallback retained-adapter disposition:
    closed_with_adapter_preserved_mapping_permanently_diagnostic_only
```

`adapter_default_dependency_count` remains a derived alias of `default_path_legacy_fallback_reach_count`. It is included here only as a continuity check against the sealed metadata-migration readpoint and cannot independently authorize adapter removal. The decisive removal gates are the explicit adapter dynamic reach probe plus adapter writer/default dependency audits.

Validation:

* Probe result records static and dynamic values separately.
* Docs references and test fixtures are not misclassified as default runtime/build dependency.
* Non-zero dynamic dependency automatically activates the fallback retained-adapter disposition branch.

---

### Change 3

Purpose:

Physically remove adapter surface only if Phase 2 PASSes.

Files:

* Adapter implementation files identified in Phase 1.
* Adapter imports, registrations, facades, aliases, and callsites identified in Phase 1.
* Adapter-specific tests or fixtures identified in Phase 1.
* `phase3_adapter_removal/removal_diff.json`
* `phase3_adapter_removal/post_removal_static_audit.json`
* `phase3_adapter_removal/post_removal_dynamic_probe.json`

Implementation Notes:

* Remove adapter implementation files.
* Remove adapter imports, callsites, registrations, facades, and aliases.
* Convert adapter-specific tests to native-path tests where they still cover current behavior.
* Test conversion is limited to mechanical import/call target replacement.
* Assertion restructuring, broad test logic rewrites, or new native-path behavioral proof design are outside this round; if needed, open a separate round or document the removed adapter-only test with preserved current-invariant coverage.
* Remove tests only when they exclusively assert transitional adapter behavior.
* Split any adapter fixture that is mixed with diagnostic mapping fixture before deletion.
* Clean stale code comments and docs references only when they imply adapter is still active.
* Preserve historical artifacts and staging traces unless they are active code/test/docs surfaces in this round.

Validation:

* Adapter implementation/import/callsite residue is `0` for active code.
* Dynamic probe remains `0`.
* Native `body_plan` path unchanged.
* Selected-role files/fields untouched.
* Full unittest suite is OK.
* Any test-count decrease is justified as removal of deleted transitional adapter behavior, with equivalent current-invariant coverage preserved or explicitly documented.

---

### Change 4

Purpose:

Seal legacy compatibility mapping as a permanent diagnostic-only non-authority fixture.

Files:

* Mapping module/docstring/metadata discovered in Phase 1.
* Diagnostic resolver tests and invariant tests discovered or added during execution.
* `phase4_mapping_seal/mapping_isolation_boundary_spec.md`
* `phase4_mapping_seal/static_isolation_audit.json`
* `phase4_mapping_seal/dynamic_isolation_audit.json`
* `phase4_mapping_seal/regression_invariant_test_report.json`

Implementation Notes:

Define diagnostic-only as:

```text
allowed reach path:
  explicit diagnostic resolver mode
  --mode diagnostic_resolver
  resolver_authority_mode='diagnostic'

violation reach path:
  default resolver path
  writer path
```

Required fixture status:

```text
legacy compatibility mapping = permanent diagnostic-only non-authority fixture
mapping writer dependency = 0
mapping default authority count = 0
DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL = retained
diagnostic output root guard = retained
```

Validation:

* Static import graph proves mapping isolation from default resolver path.
* Writer path cannot import or execute mapping.
* Dynamic default mode trace proves mapping code is not entered.
* Explicit diagnostic mode can still reach mapping under output-root guard.
* Regression tests include intentional fail-loud default legacy label scenarios.

---

### Change 5

Purpose:

Seal selected-role negative invariant preservation.

Files:

* `phase5_selected_role_invariant/selected_role_dependency_map.json`
* `phase5_selected_role_invariant/pre_post_comparison.json`
* `phase5_selected_role_invariant/native_authority_preservation_seal.json`

Implementation Notes:

Compare pre/post values:

```text
selected_role_precedence_default_influence_count
selected_role_target_default_influence_count
selected_role_target_legacy_authority_count
selected_role_target_masked_legacy_fallback_reach_count
```

Also verify that `selected_role`, `selected_role_precedence`, and `selected_role_target` files/fields were not removed, renamed, reclassified, or behaviorally redirected.

Validation:

* Selected-role influence counts are identical before and after this round.
* Non-zero dynamic influence remains native authority evidence.
* No selected-role cleanup, removal, or zeroing is claimed.

---

### Change 6

Purpose:

Check diagnostic/audit capability after mapping preservation and adapter disposition.

Files:

* `phase6_diagnostic_audit_check/diagnostic_audit_retention_report.json`
* `phase6_diagnostic_audit_check/adapter_removal_audit_loss_assessment.md`

Implementation Notes:

* Run legacy label rejection diagnostic tests.
* Run diagnostic resolver mode fixtures.
* Verify diagnostic report generation without adapter if adapter was removed.
* List audit surfaces removed with adapter.
* Declare audit loss status:

```text
audit_loss = none
```

or:

```text
audit_loss = accepted
accepted_reason = "<bounded reason>"
```

Accepted audit loss boundary:

* The removed surface was adapter-only diagnostic scaffolding with no default-path, writer-path, or public-facing dependency.
* The same current invariant is still auditable through a native-path probe, mapping isolation audit, or hard-gate report.
* The loss does not remove legacy-label fail-loud coverage.
* The loss does not remove diagnostic output-root guard coverage.
* The loss does not remove selected-role preservation evidence.
* The loss is internal-only and has no active consumer outside this round's diagnostic artifacts.

Authority boundary:

* Planning authority alone cannot declare `audit_loss = accepted`.
* `audit_loss = accepted` requires Phase 8 adversarial review PASS or conditional PASS with the audit-loss reason explicitly accepted.
* If a removed adapter audit surface is required and has no native-path replacement, the branch must fail Phase 6 and either restore the adapter surface or close as partial/blocked.
* Phase 10 closeout must include explicit fields for `audit_loss`, `accepted_reason`, removed audit surfaces, replacement evidence, and Phase 8 review disposition.

Validation:

* Diagnostic legacy mapping fixture remains usable.
* No adapter-dependent diagnostic path remains after removal branch.
* Preservation branch explicitly states adapter is retained because dynamic dependency was non-zero.
* Diagnostic output root guard remains enforced.

---

### Change 7

Purpose:

Run the Phase 7 hard gate.

Files:

* `phase7_hard_gate/hard_gate_report.json`
* `phase7_hard_gate/rendered_delta_audit.json`
* `phase7_hard_gate/lua_bridge_hash_audit.json`
* `phase7_hard_gate/test_run_report.json`

Implementation Notes:

Required invariant:

```text
rendered_delta_count = 0
Lua/runtime = unchanged
default_path_legacy_fallback_reach_count = 0
adapter_default_dependency_count = 0
adapter_writer_dependency_count = 0
legacy_mapping_default_authority_count = 0
selected_role files/fields = untouched
test run = full unittest suite OK
guard-round invariant coverage = preserved
```

Validation command:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Additional validation must rerun dynamic dependency measurement for adapter and selected-role invariants.

Validation:

* All required invariants pass.
* Any rendered/Lua/test/dynamic failure blocks closeout until phase-level cause is identified and reverted or repaired.

---

### Change 8

Purpose:

Perform adversarial review of Phase 1-7 evidence.

Files:

* `phase8_review/adversarial_review.md`

Implementation Notes:

Review format:

```text
Good points
Critical
Important
Minor
PASS / FAIL
```

Decision rule:

```text
single resolvable Critical -> conditional PASS allowed
multiple Critical findings -> FAIL
```

Conditional PASS follow-up rule:

```text
If Phase 8 returns conditional PASS for a single resolvable Critical, closeout may proceed only through one sealed path:
  (a) rerun the affected phase and replace the Critical with PASS evidence, or
  (b) create a Phase 10 patch-phase entry that resolves the Critical before final closeout, or
  (c) explicitly defer the Critical and mark this round partial, not complete.
```

Conditional PASS cannot silently become complete closeout. The chosen path must be recorded in `phase8_review/adversarial_review.md` and mirrored in the Phase 10 closeout packet.

Validation:

* PASS or conditional PASS is required before documentation closeout.
* Any Critical must name the phase artifact and exact resolution condition.
* Conditional PASS must name the follow-up path `(a)`, `(b)`, or `(c)`.

---

### Change 9

Purpose:

Document final disposition in canonical docs after hard gate and review pass.

Files:

* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* `docs/ARCHITECTURE.md`
* `phase9_documentation/decisions_entry.md`
* `phase9_documentation/roadmap_addendum_ledger_entry.md`
* `phase9_documentation/architecture_closeout_note.md`

Implementation Notes:

DECISIONS entry must be a new dated entry, not an amendment to #41, #42, or #43.

ARCHITECTURE.md boundary:

```text
ARCHITECTURE.md changes must not amend sealed sections.
Allowed edits:
  append a closeout note to an unsealed current readpoint section
  add a new bounded current-readpoint paragraph
  add a ledger entry that points to the new decision
Forbidden edits:
  rewriting sealed #41 / #42 / #43 semantics
  changing selected-role native authority wording
  changing diagnostic guard closeout wording
  turning this disposition into runtime/deployed/readiness authority
```

If execution requires a sealed-section amendment, Phase 9 fails and a separate governance decision is required before continuing.

Required decision language:

```text
legacy compatibility mapping is permanently retained as a diagnostic-only non-authority fixture
adapter surface is removed as a post-migration transitional residue
Resolver Compatibility / Adapter Cleanup category is closed
```

Required non-decision language:

```text
selected_role removal 아님
mapping deletion 아님
complete-removal cleanup opening 아님
runtime Lua regeneration 아님
deployed closeout / ready_for_release 아님
```

Required reopen triggers:

* Retained mapping re-enters default path or writer path.
* Hidden default/writer adapter dependency appears after removal.
* Diagnostic fixture function is lost and needed audit cannot be performed.
* Selected-role authority is architecturally redefined in a future round.
* Explicit diagnostic resolver mode is retired.
* Legacy compatibility surface is exposed again through a new default input format.
* A future deletion/removal goal is explicitly opened by a new decision.
* Outside these triggers, this category is not reopened.

Validation:

* Docs do not claim runtime QA, deployed closeout, Workshop readiness, or `ready_for_release`.
* Mapping preservation is not described as unfinished cleanup.
* Adapter removal is not inflated into external compatibility or release readiness.
* ARCHITECTURE.md edits are limited to unsealed current-readpoint closeout notes or additive ledger entries.

---

### Change 10

Purpose:

Create final closeout packet.

Files:

* `phase10_closeout/final_disposition_closeout.json`
* `phase10_closeout/final_disposition_closeout.md`
* `phase10_closeout/touched_surface_manifest.json`
* `phase10_closeout/validation_summary.md`

Implementation Notes:

Closeout packet must include:

* phase artifact manifest
* touched surface list
* mutation/no-change disclosure
* validation commands and outputs
* branch state:

```text
closed_with_adapter_removed_mapping_permanently_diagnostic_only
```

or:

```text
fallback retained-adapter disposition:
  closed_with_adapter_preserved_mapping_permanently_diagnostic_only
```

* explicit claim ceiling:

```text
No runtime Lua regeneration.
No deployed closeout.
No manual in-game QA pass.
No Workshop release readiness.
No ready_for_release claim.
No full runtime equivalence claim.
No full external compatibility preservation claim.
```

Validation:

* All required invariants are linked to evidence artifacts.
* No undeclared mutation exists.
* No runtime/deployed/release claim leaks into closeout wording.

---

## 7. Validation Plan

### Automated Validation

Required command:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Required result:

```text
full unittest suite OK
```

Baseline comparison:

```text
guard-round baseline was 386 tests / OK
```

Test-count decrease is allowed only if:

* removed tests exclusively covered deleted adapter transitional behavior, and
* equivalent current-invariant coverage is preserved or explicitly documented.

Hard blockers:

* failing tests
* missing legacy-label fail-loud test
* missing diagnostic output-root guard test
* missing adapter dependency probe
* missing selected-role invariant comparison

Required audits:

* Baseline hash audit.
* Adapter static surface audit.
* Adapter dynamic reach probe before removal.
* Adapter dynamic reach probe after removal, if removal branch executes.
* Mapping static isolation audit.
* Mapping dynamic isolation audit.
* Diagnostic resolver mode output-root guard test.
* Legacy label default fail-loud regression test.
* Rendered text diff against Phase 1 baseline.
* Lua bridge output hash diff against Phase 1 baseline.
* Selected-role pre/post influence comparison.
* Touched surface manifest review.

### Manual Validation

Manual validation in this round is limited to artifact review:

* Phase artifact inspection.
* Diff review.
* Adversarial review.
* Documentation language review.

No manual in-game QA pass is performed or claimed.

### Validation Limits

This round will not perform:

* In-game runtime QA.
* Multiplayer validation.
* Long-session runtime validation.
* External mod compatibility sweep.
* Workshop packaging validation.
* Deployment validation.
* Full runtime equivalence proof.
* Full historical artifact cleanup proof.
* Full compatibility preservation proof.

---

## 8. Risk Surface Touch

### Authority Surface

Touched only as negative preservation evidence.

* Default resolver authority must remain native v2 / body_plan aligned.
* Legacy mapping must not become default authority.
* Selected-role authority / trace must remain unchanged.
* Adapter removal must not introduce a new fallback or silently alter resolver behavior.

### Runtime Behavior Surface

Expected none.

* Runtime Lua regeneration is forbidden.
* Lua bridge hash must remain unchanged.
* Rendered delta must remain `0`.
* No deployed runtime artifact should be edited.

### Compatibility Surface

Touched.

* Legacy compatibility mapping is retained as diagnostic-only fixture.
* Adapter surface is removed only after dynamic reach PASS.
* If dynamic dependency is found, adapter is preserved and sealed instead.
* External mod compatibility is not comprehensively measured.

### Sealed Artifact Surface

Protected.

* Generated runtime Lua artifacts are not regenerated.
* Quality/publish state artifacts are not modified.
* Facts layer is not repaired.
* Staging artifacts are added only under this round's diagnostic root.

### Public-Facing Output Surface

Expected none.

* Rendered text delta must be `0`.
* User-facing Lua/runtime output remains unchanged.
* No release-facing language is introduced.

---

## 9. Risk Analysis

### Architecture Risk

* Adapter removal could accidentally become resolver authority redesign.
* Mapping preservation could be misread as default fallback permission.
* Selected-role native authority could be reopened as cleanup target.
* Docs could blur the distinction between #42 guard closeout and this final disposition closeout.

### Runtime Risk

* A hidden adapter dependency could affect rendered output despite static residue appearing safe.
* Runtime Lua files could be touched accidentally during validation or formatting.
* Lua bridge hash comparison could be invalid if Phase 1 baseline is poorly sealed.

### Compatibility Risk

* Removing adapter may remove a diagnostic reproduction path that tests do not cover.
* Retained mapping may look like unresolved debt unless its permanent diagnostic-only status is explicit.
* Historical adapter traces may be over-cleaned and harm audit provenance.

### Regression Risk

* Legacy label fail-loud guard could regress.
* Diagnostic output-root guard could regress.
* Writer path could indirectly reach mapping through a hidden import.
* Selected-role influence counts could drift, turning this round into an unintended authority change.

---

## 10. Rollback Plan

Rollback applies only to the adapter removal branch.

Do not rollback:

* selected-role native authority seal
* diagnostic-only mapping boundary
* default resolver fail-loud guard

Branch handling:

```text
Phase 2 probe FAIL:
  skip Phase 3
  close as fallback retained-adapter disposition:
    closed_with_adapter_preserved_mapping_permanently_diagnostic_only

Phase 3 static/dynamic audit FAIL:
  revert adapter removal diff
  restore Phase 1 baseline
  fallback to adapter preserved branch

Phase 3 deletes mapping diagnostic fixture accidentally:
  revert adapter removal diff
  restore mapping diagnostic-only boundary
  lower adapter to temporary retained diagnostic-only surface
  document hidden dependency

Phase 4 mapping isolation audit FAIL:
  redefine mapping isolation boundary and rerun Phase 4
  if impossible, hold this round and open a future mapping deletion/design round separately

Phase 5 selected-role drift:
  classify adapter removal as silent authority change
  revert Phase 3
  hold adapter removal disposition for a future round

Phase 7 hard gate FAIL:
  identify introducing phase
  revert or repair at phase level
  rerun relevant audits
```

Possible rollback closeout states:

```text
partial:
  mapping retained as diagnostic-only fixture
  adapter removal blocked by hidden dependency

blocked:
  adapter hidden default/writer dependency found
```

Mapping preservation remains the selected disposition even if adapter removal rolls back.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke / SPI boundaries must not be violated.
* Iris runtime/build separation must remain intact.
* Current default compose authority must remain intact.
* `selected_role`, `selected_role_precedence`, and `selected_role_target` must remain untouched native resolver authority / trace.
* Legacy mapping must not re-enter default authority.
* Retained mapping must remain diagnostic-only / non-authority / non-writer.
* Adapter removal must not become resolver authority redesign.
* Rendered delta must be `0`.
* Lua/runtime must remain unchanged.
* `default_path_legacy_fallback_reach_count = 0` must remain true.
* `default_adapter_dependency_count = 0` must remain true.
* Adapter writer dependency must remain `0`.
* Diagnostic resolver mode and output-root guard must remain enforced.
* Runtime Lua regeneration is forbidden.
* Deployed closeout and `ready_for_release` declarations are forbidden.
* Single-writer principle must hold: compose, normalizer, linter, and rendered phases must not mutate quality or publish state.
* Dual-zero gate model must hold: static count and dynamic execution reach are independent gates.
* Sealed decisions #41, #42, and #43 must not be amended in this round; only a new dated entry is allowed.
* Facts immutability must hold: facts layer is not a downstream fix target in this round.

---

## 12. Expected Closeout State

Expected complete closeout on probe PASS:

```text
complete:
  closed_with_adapter_removed_mapping_permanently_diagnostic_only
```

Meaning:

* Option C is closed.
* Legacy compatibility mapping is permanently retained as diagnostic-only non-authority fixture.
* Adapter surface is removed as post-migration transitional residue.
* Resolver Compatibility / Adapter Cleanup category is closed.
* Selected-role authority / trace remains unchanged.
* Rendered delta is `0`.
* Lua/runtime is unchanged.
* Full unittest suite is OK and guard-round invariant coverage is preserved.
* No deployed closeout or `ready_for_release` is claimed.

Fallback retained-adapter closeout on probe FAIL:

```text
complete:
  closed_with_adapter_preserved_mapping_permanently_diagnostic_only
```

Meaning:

* Mapping disposition still closes as permanent diagnostic-only preservation.
* Adapter is preserved because non-zero dynamic dependency made removal unsafe in this round.
* Preservation branch is not ad-hoc; it is pre-sealed by Phase 2 branch rules.
* This is an accepted fallback retained-adapter disposition, not Option C success.
* No adapter removal claim is made.
* The category closes only if adapter preservation is explicitly documented with hidden dependency evidence and default/writer non-authority boundaries.

Blocked or partial closeout is allowed only if Phase 4 mapping isolation cannot be proven, Phase 5 selected-role drift appears, or Phase 7 hard gate cannot be repaired without changing the round's authority boundary.
