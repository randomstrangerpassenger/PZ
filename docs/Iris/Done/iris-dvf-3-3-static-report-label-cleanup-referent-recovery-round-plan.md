# Iris DVF 3-3 Static Report Label Cleanup Referent Recovery Round Plan

> 상태: Draft v0.2-plan  
> 기준일: 2026-05-20  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `Roadmap - Iris DVF 3-3 Static Report Label Cleanup Referent Recovery Round` (2026-05-20 user-provided roadmap)  
> 직접 상위 결정:
> - 2026-05-20 - Static Report Label Cleanup no-residue closeout is insufficient for the original cleanup intent
> - 2026-05-20 - Generated report / operator label cleanup requires preflight scope lock before mutation
> - 2026-05-19 - Runtime Payload Enum Rename Scope Round closes as Branch B/B1
> - 2026-04-26 - DVF 3-3 runtime_state vocabulary remapped to adopted/unadopted
> 계획 형식: `docs/PLAN_TEMPLATE.md`  
> template attestation: `docs/PLAN_TEMPLATE.md` exists in the current workspace and this plan follows Section 0 disclosure plus the 1-12 section structure in that template.  
> 실행 상태: planning authority only. 이 문서는 referent recovery round의 실행 계획이며, 작성 시점에는 source decisions, runtime Lua, rendered output, generated report artifacts, staging evidence, or top-doc closeout state를 변경하지 않는다.

---

## 0. Round Opening Disclosure

Round name:

```text
Iris DVF 3-3 Static Report Label Cleanup Referent Recovery Round
```

Opening rule:

```text
Phase 1 MUST NOT start until Phase 0 creates the round-local opening decision
artifacts and records the authority chain that makes this a referent recovery round,
not a lexical cleanup round.
```

Required Phase 0 opening artifacts:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase0_opening/opening_decision.md
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase0_opening/opening_decision.json
```

Execution scale:

```text
governance
```

If Phase 3 proves that all relevant artifacts are non-authoritative diagnostic-only artifacts, the closeout may explain that the effective mutation surface was narrower. The opening scale remains governance because the round initially touches generated reports, operator-facing artifacts, sealed artifact interpretation, closeout state mapping, and top-doc meaning.

Authority source and ownership:

```text
docs/Philosophy.md
  > docs/DECISIONS.md
  > docs/ARCHITECTURE.md
  > docs/ROADMAP.md
  > approved roadmap / approved plan
```

Canonical readpoint:

```text
runtime_state canonical enum = adopted / unadopted
legacy active / silent = diagnostic / import / historical read-only alias only
```

Round purpose:

```text
Recover or disprove the original generated report / operator-facing artifact
referent before making any cleanup claim.
```

Mutable surfaces:

* Round-local staging artifacts under:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/
```

* Referent discovery inventory and VCS trace reports.
* Occurrence classification reports and mutation target manifests.
* Branch B only: the confirmed generated report/operator artifact, or its single approved writer/recipe, after occurrence-level mutation target lock.
* Phase 8 only: append-only top-doc addenda in `docs/DECISIONS.md`, `docs/ROADMAP.md`, and `docs/ARCHITECTURE.md` only if current readpoint text is affected.

Immutable surfaces:

* `docs/DECISIONS.md` historical decision bodies.
* 2026-04-26 terminology migration note body.
* `docs/DECISIONS.md` `증거:` path/hash locked artifacts.
* Runtime Lua chunk topology and staged/workspace Lua hashes.
* 2105-row source decision identity and rendered text.
* `runtime_state`, `quality_state`, and `publish_state` semantics.
* `selected_role`, `selected_role_precedence`, and `selected_role_target` native resolver authority.
* Browser / Wiki / Tooltip runtime behavior.
* Diagnostic/import/historical alias support for legacy `active / silent`.

Intended closeout ceiling:

```text
static/generated artifact cleanup closeout
```

This round must not claim runtime rollout, deployed closeout, Workshop release, manual in-game QA pass, or `ready_for_release`.

Branch outcomes:

| Branch | Closeout | Meaning |
|---|---|---|
| A | `closed_with_referent_confirmed_no_current_label_residue` | Referent is confirmed and referent-scoped current-label residue is `0`. |
| B | `closed_with_referent_confirmed_and_rewritten` | Referent is confirmed, residue is found, and direct approved artifact patch removes only target occurrences. |
| B | `closed_with_referent_confirmed_and_canonically_regenerated` | Referent is confirmed, residue is found, and canonical writer/recipe regeneration removes only target occurrences. |
| C | `closed_obsoleted_by_artifact_removal` | Referent existed historically but is removed/obsolete and no longer generated or consumed. This is not cleanup success. |
| D | `blocked_missing_original_operator_artifact_referent` | Referent cannot be recovered after required absence proof. |
| D | `blocked_regeneration_recipe_missing` | Candidate requires regeneration proof but recipe is missing. |
| D | `blocked_unknown_authority` | Occurrence or artifact authority cannot be classified safely. |
| D | `blocked_referent_input_missing` | Required referent input artifacts are unavailable. |
| D | `blocked_referent_ambiguous` | Multiple plausible referents cannot be separated. |
| D | `blocked_absence_proof_incomplete` | Four-lane discovery/absence proof, VCS trace, regeneration attempt, or scope definition proof is incomplete. |

Failure semantics:

```text
opening decision missing -> blocked_opening_decision_missing
prior round reconstruction incomplete -> blocked_prior_round_reconstruction_incomplete
referent input missing -> blocked_referent_input_missing
referent ambiguous -> blocked_referent_ambiguous
four-lane absence proof incomplete -> blocked_absence_proof_incomplete
unknown authority occurrence -> blocked_unknown_authority
historical body mutation required -> blocked_historical_body_mutation_required
historical body diff -> blocked_historical_body_mutation
sealed evidence hash delta -> blocked_sealed_evidence_mutation
non-label payload delta -> blocked_non_label_delta
runtime/source/rendered/state delta -> blocked_invariant_delta
validation command unavailable -> blocked_validation_tool_missing
```

---

## 1. Objective

The objective of this execution plan is to recover the original generated report / operator-facing artifact referent behind the `active / silent` label cleanup concern, then close the issue according to evidence rather than according to a current checkout lexical zero.

This round closes one of these claims only:

```text
The original artifact referent is confirmed and has no current-label residue.
The original artifact referent is confirmed and its current-label residue was cleaned.
The original artifact referent is confirmed obsolete by removal and cleanup is not claimed.
The original artifact referent cannot be recovered and cleanup is blocked, not complete.
```

The round does not reopen DVF 3-3 runtime payload enum migration. Current canonical runtime payload enum remains `adopted / unadopted`, and legacy `active / silent` remains allowed only as diagnostic/import/historical read-only alias.

---

## 2. Scope

In scope:

* Phase 0 governance opening and scope lock.
* Reconstruction of the previous `Static Report Label Cleanup Round` scan universe and Surface C definition.
* Discovery of referent candidates across four lanes:
  * current checkout lexical/path scan,
  * staging/archive/backup scan,
  * VCS trace scan,
  * generation recipe/script scan.
* Classification of candidate artifacts as current, moved, deleted, generated, diagnostic-only, historical trace, unrelated, or unrecoverable.
* Occurrence-level classification for confirmed referents only.
* Branch B only: exact mutation or canonical regeneration for confirmed `current_operator_label_residue`.
* Invariant and hard-gate verification for source, rendered, runtime, state, historical, and alias preservation surfaces.
* Adversarial review focused on false cleanup success, false no-residue, and false closeout branch selection.
* Evidence-bounded closeout with append-only top-doc updates after gates pass.

Positive referent rule:

```text
An artifact is not the referent merely because it contains active/silent.
It must be tied to the original generated report / operator-facing artifact concern
by path, context, VCS trace, prior round gap analysis, writer/recipe evidence,
or an explicitly documented evidence chain.
```

Mutation rule:

```text
No mutation is permitted before referent classification and occurrence-level
mutation target manifest are complete.
```

### Explicitly Out Of Scope

* Runtime Lua regeneration or redeployment.
* Runtime payload enum migration reopening.
* Source decisions rewrite.
* 2105-row row identity change.
* Rendered text rebaseline.
* `quality_state` or `publish_state` change.
* Browser / Wiki / Tooltip consumer policy change.
* Historical sealed decision body rewrite.
* Diagnostic/import alias removal.
* Repo-wide `active / silent` zero target.
* Adapter/resolver/selected_role cleanup reopening.
* Silent 21 metadata cleanup reopening.
* Release readiness, deployed closeout, manual in-game QA pass, or Workshop release declaration.
* Future builder output guard as an automatic completion condition.

---

## 3. Non-Goals

This plan does not attempt to:

* Prove that every `active` or `silent` string in the repository is gone.
* Convert metric keys, diagnostic aliases, import aliases, historical readpoints, or unrelated English words.
* Reinterpret `closed_with_no_current_operator_residue_found` as actual artifact cleanup completion.
* Create a new mapping authority beyond the already adopted `active -> adopted` and `silent -> unadopted` runtime_state vocabulary.
* Change DVF 3-3 runtime behavior or user-facing Lua behavior.
* Promote any static validation result to release readiness.

---

## 4. Assumptions

* All required project documents are under `docs/` unless an execution prompt explicitly specifies another path.
* The user-provided roadmap is the immediate approved planning input for this plan draft.
* If `docs/DECISIONS.md` or `docs/ARCHITECTURE.md` do not yet contain the full 2026-05-20 referent-recovery-first readpoint, Phase 0 must record this as round-local opening authority and Phase 8 may add append-only top-doc updates after gates pass.
* The earlier no-residue closeout is treated by this plan as current-checkout Surface C preflight evidence only, not as actual original artifact cleanup completion.
* Current DVF 3-3 baseline is `2105` rows with `adopted 2084 / unadopted 21`.
* Legacy `active / silent` may still appear in allowed diagnostic/import/historical contexts.
* Current checkout may not contain the original problem artifact.
* The actual execution environment has access to local Git history needed for VCS trace scans.
* If a required tool is missing, validation is blocked rather than treated as passed.

---

## 5. Repository Areas Affected

### Code

Potentially affected only in Branch B after referent and mutation target lock:

* `Iris/build/description/v2/tools/build/build_static_report_label_cleanup_referent_recovery_round.py`
* The confirmed single-writer report generator or recipe, if the referent is generated and writer patch is selected.

### Docs

Plan created by this task:

* `docs/Iris/iris-dvf-3-3-static-report-label-cleanup-referent-recovery-round-plan.md`

Possible execution closeout addenda after hard gates:

* `docs/DECISIONS.md`
* `docs/ROADMAP.md`
* `docs/ARCHITECTURE.md` only if current readpoint text needs adjustment.

### Config

None expected.

### Generated Artifacts

Round-local staging root:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/
```

Expected execution artifacts:

```text
phase0_opening/opening_decision.md
phase0_opening/opening_decision.json
phase1_prior_round_reconstruction.json
phase1_surface_c_universe.md
phase1_gap_hypotheses.json
phase2_referent_candidate_inventory.jsonl
phase2_vcs_trace_report.md
phase2_regeneration_recipe_candidates.json
phase3_referent_classification.json
phase3_referent_decision.md
phase4_occurrence_inventory.jsonl
phase4_occurrence_classification.json
phase4_mutation_target_manifest.json
phase5_patch_delta_report.json
phase5_regeneration_delta_report.json
phase6_invariant_report.json
phase6_hard_gate_report.json
phase7_adversarial_review.md
phase8_closeout.json
phase8_closeout.md
```

Branch C/D may skip Phase 4/5 mutation artifacts when referent status makes occurrence inventory or mutation inapplicable; the skip reason must be explicit.

---

## 6. Planned Changes

### Change 1 - Phase 0 Opening / Scope Lock

Purpose:

* Open the round as referent recovery, not simple lexical cleanup.
* Lock execution scale, mutable/immutable surfaces, validation ceiling, closeout ceiling, and failure semantics.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase0_opening/opening_decision.md
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase0_opening/opening_decision.json
```

Implementation Notes:

* Cite `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and this approved plan.
* Explicitly state that historical sealed body mutation is forbidden.
* Explicitly state that runtime Lua regeneration is out of scope.
* Record the four possible branch families A/B/C/D.

Validation:

* Opening decision contains execution scale, mutable surface, immutable surface, validation ceiling, closeout ceiling, and failure semantics.
* Authority chain is present.
* No mutation target is declared in Phase 0.

---

### Change 2 - Phase 1 Prior Round Reconstruction

Purpose:

* Reconstruct what the previous `Static Report Label Cleanup Round` actually scanned, what it did not scan, and why `rewrite target 0` was insufficient for original cleanup intent.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_round/
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase1_prior_round_reconstruction.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase1_surface_c_universe.md
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase1_gap_hypotheses.json
```

Implementation Notes:

* Inspect at minimum:

```text
phase1_inventory/
phase2_scope_lock/
phase2_mutation_target_manifest.*
phase3_mutation/
phase6_adversarial_review/
phase7_closeout/
```

* Reconstruct previous Surface C definition and current checkout Surface C universe.
* `phase1_prior_round_reconstruction.json` must contain an explicit closeout-name contrast:

```text
prior_round_closeout_name = closed_with_no_current_operator_residue_found
prior_round_evidence_basis = current checkout Surface C preflight rewrite target 0
this_round_branch_a_closeout_name = closed_with_referent_confirmed_no_current_label_residue
this_round_branch_a_evidence_basis = confirmed referent-scoped current-label residue 0
same_meaning = false
```

* Record gap hypotheses:

```text
artifact_absent
artifact_renamed
artifact_archived
artifact_ignored_or_untracked
artifact_generated_but_recipe_missing
artifact_outside_surface_c
historical_or_diagnostic_usage_misread_as_current_label
```

Validation:

* Each hypothesis has `evidence`, `refuted`, or `unknown`.
* Prior closeout limitation is documented as preflight scope evidence only.
* The two closeout names above are present in `phase1_prior_round_reconstruction.json` and explicitly marked as different evidence bases.

---

### Change 3 - Phase 2 Candidate Discovery

Purpose:

* Discover possible original referents across current checkout, staging/archive/backup, VCS history, and writer/recipe surfaces.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase2_referent_candidate_inventory.jsonl
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase2_vcs_trace_report.md
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase2_regeneration_recipe_candidates.json
```

Implementation Notes:

* Lane 1 - current checkout lexical/path scan:

```text
active
silent
adopted
unadopted
operator
generated report
static report
label
Surface C
residue
```

* Lane 1 filename candidates:

```text
*report*.json
*report*.md
*operator*.json
*operator*.md
*label*.json
*surface*.json
*inventory*.json
*residue*.json
*scope*.json
*mutation*.json
```

* Lane 2 - staging/archive/backup scan:

```text
Iris/build/description/v2/staging/
Iris/build/description/v2/staging/compose_contract_migration/
_archive
backup
Done/Walkthrough
docs/Iris
```

* Lane 2 must also record ignored/untracked evidence with `git status --ignored --short` or an equivalent local evidence command, so ignored or untracked generated artifacts are not silently excluded.

* Lane 3 - VCS trace scan:

```text
git log --all --name-status -- Iris/build/description/v2
git log --all --name-only -- '*report*' '*operator*' '*static*' '*label*'
git grep -n -I -E 'active|silent|adopted|unadopted' -- Iris docs
git grep -n -I -E 'operator|generated report|Surface C|static report|label cleanup' -- Iris docs
git log --all --diff-filter=D --name-only -- Iris/build/description/v2
git log --all --follow -- <candidate_path>
```

* Lane 4 - recipe/script scan:

```text
report writer
static report generator
operator artifact builder
validation report generator
cleanup inventory builder
```

* For each candidate, record path, status, producer script, consumer surface, occurrence count, VCS evidence, and likely original referent score.

Validation:

* All four discovery lanes are executed or explicitly blocked.
* Candidate inventory is JSONL and contains a stable candidate id for every candidate.
* VCS trace report distinguishes current, deleted, moved, and renamed evidence.

---

### Change 4 - Phase 3 Referent Classification

Purpose:

* Confirm the original referent, prove artifact removal/obsolescence, or fail loud with a blocked branch.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase3_referent_classification.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase3_referent_decision.md
```

Implementation Notes:

* Classify each candidate as one of:

```text
confirmed_current_referent
confirmed_moved_referent
confirmed_deleted_referent
confirmed_generated_referent
candidate_but_not_original
diagnostic_only_non_authority_artifact
historical_trace_only
unrelated
unrecoverable_referent_gap
```

* Referent confirmation must use multiple evidence lanes, not a single lexical match.
* Absence proof requires all four discovery lanes to be completed or explicitly named as blocked, plus VCS trace, regeneration attempt, and scope definition check.
* Phase 3 chooses Branch A/B/C/D.

Validation:

* Confirmed branch has one primary referent or a clearly bounded referent set.
* Branch C records current consumption as false.
* Branch D records which of the four discovery/absence-proof lanes failed or completed, and names any lane that blocks absence proof.

---

### Change 5 - Phase 4 Occurrence-level Inventory

Purpose:

* For confirmed referents only, classify each `active / silent` occurrence before any mutation.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase4_occurrence_inventory.jsonl
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase4_occurrence_classification.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase4_mutation_target_manifest.json
```

Implementation Notes:

* Skip Phase 4 for Branch C/D unless a bounded occurrence inventory is still needed to explain the branch.
* Classify occurrences as:

```text
current_operator_label_residue
historical_sealed_body
diagnostic_alias
import_alias
metric_legacy_count
runtime_state_historical_readpoint
generated_count_label
test_fixture
unrelated_word
unknown_authority
```

* Only `current_operator_label_residue` may enter the mutation target manifest.
* If any occurrence is `unknown_authority`, mutation is blocked.

Validation:

* Target manifest includes occurrence id, file path, old text, proposed new text, reason, and authority.
* Target count `0` with confirmed referent moves to Branch A.
* Target count greater than `0` moves to Branch B.

---

### Change 6 - Phase 5 Mutation or Canonical Regeneration

Purpose:

* Remove confirmed current operator label residue only when Branch B is selected.

Files:

Branch B-1 direct patch:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase5_patch_delta_report.json
```

Branch B-2 writer/recipe patch:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase5_regeneration_delta_report.json
```

Implementation Notes:

* Branch B-2 is the default path when the confirmed referent is a generated artifact: patch the single approved writer/recipe and regenerate the artifact.
* Branch B-1 may patch only target occurrences approved in Phase 4 and only when writer/recipe patching is proven unavailable, obsolete, or unsafe for the confirmed referent.
* If Branch B-1 is selected, `phase5_patch_delta_report.json` must include `writer_patch_impossible_reason`.
* Generated authoritative artifacts should be changed by writer/recipe by default, not by hand.
* Non-target `active / silent` occurrences must remain unchanged.
* Branch A/C/D perform no mutation.

Validation:

* Actual changed occurrence count equals target occurrence count.
* Old/new diff contains no non-label payload delta.
* Source decisions, rendered text, runtime Lua, row identity, `quality_state`, and `publish_state` remain unchanged.

---

### Change 7 - Phase 6 Invariant and Hard Gate Verification

Purpose:

* Prove the round stayed inside static/generated report/operator label cleanup boundaries.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase6_invariant_report.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase6_hard_gate_report.json
```

Implementation Notes:

* Verify:

```text
row count 2105 unchanged
row identity unchanged
rendered text unchanged
runtime Lua/chunk topology unchanged
quality_state unchanged
publish_state unchanged
Browser/Wiki/Tooltip consumer behavior unchanged by this round
historical sealed body unchanged
diagnostic/import alias preserved
source decisions/facts unchanged
```

* File-backed immutable surfaces must use sha256 pre/post evidence at the same standard as prior sealed rounds. Where a surface is structured rather than single-file-backed, Phase 6 must record the exact comparison method, input paths, and resulting digest or no-diff proof.
* Phase 6 must record a dual-zero gate disposition:

```text
static_residue_gate = pass only when referent-scoped current operator label residue count is 0
dynamic_reach_gate = not_applicable only when the confirmed referent is static generated report/operator evidence and is not consumed at runtime
dynamic_reach_gate = pass only when a runtime-consumed referent has a separately proven current active/silent execution reach count of 0
```

* If `dynamic_reach_gate = not_applicable`, `phase6_hard_gate_report.json` must record the reason and the evidence that the referent is static-only.
* If the referent is runtime-consumed or its consumption status is unknown, a separate dynamic reach gate is required; unknown consumption blocks closeout with `blocked_unknown_authority`.
* Branch A/B must prove referent-scoped current operator label residue `0`.
* Branch C/D must not claim cleanup complete.

Validation:

```text
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

* Commands must exit code `0` to be reported as pass.
* Missing tools are blocked validation, not pass.
* `phase6_invariant_report.json` must include sha256 or explicit no-diff evidence for immutable file-backed surfaces.
* `phase6_hard_gate_report.json` must include `static_residue_gate` and `dynamic_reach_gate` objects.

---

### Change 8 - Phase 7 Adversarial Review

Purpose:

* Prevent false positive cleanup, false negative no-residue, and inflated closeout branch selection.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase7_adversarial_review.md
```

Implementation Notes:

* Review must explicitly answer:

```text
Was the original artifact referent really confirmed?
Was current checkout absence confused with cleanup completion?
If generated, was the writer/recipe checked?
Was outside-Surface-C artifact possibility closed?
Were diagnostic/import/historical aliases preserved?
Was historical sealed body untouched?
Was mutation target occurrence-level proven?
Was runtime/release/deployed closeout avoided?
For Branch D, did absence proof cover all four discovery lanes, including current checkout, staging/archive/backup, VCS trace, and recipe/script evidence?
For Branch D, did the absence proof also include VCS trace, regeneration attempt, and scope definition check, or name the blocked lane?
For Branch C, was artifact removal not treated as success?
```

Validation:

* Verdict is `PASS`, `CONDITIONAL PASS`, or `FAIL`.
* Blocker count and major count must be `0` for Branch A/B/C closeout.
* Branch D closeout requires the adversarial review to confirm that the four-lane absence proof is complete or that the exact blocked lane and blocked status are named.

---

### Change 9 - Phase 8 Closeout

Purpose:

* Close with the branch that matches the evidence and record non-decisions.

Files:

```text
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase8_closeout.json
Iris/build/description/v2/staging/compose_contract_migration/static_report_label_cleanup_referent_recovery_round/phase8_closeout.md
docs/DECISIONS.md
docs/ROADMAP.md
docs/ARCHITECTURE.md
```

Implementation Notes:

* `docs/DECISIONS.md` and `docs/ROADMAP.md` updates are append-only.
* `docs/ARCHITECTURE.md` updates only if current readpoint text is affected.
* Closeout must state referent status, mutation status, residue status, unchanged surfaces with hash/no-diff evidence summary, dual-zero gate disposition, validation commands/results, and non-decisions.
* Runtime rollout, deployed closeout, Workshop release, manual QA, and `ready_for_release` must be `not_claimed`.

Validation:

* Closeout branch matches Phase 3/4/5/6/7 evidence.
* Obsoleted or blocked branches do not claim cleanup complete.

---

## 7. Validation Plan

### Automated Validation

Required execution commands:

```text
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Required static/evidence checks:

* Phase 0 opening artifact schema/content check.
* Phase 1 prior round reconstruction completeness check.
* Phase 2 four-lane discovery completion check.
* Phase 3 referent confirmation or absence proof check.
* Phase 4 occurrence manifest schema check for Branch A/B.
* Branch B mutation/regeneration delta check.
* Source decisions unchanged check.
* Row count `2105` unchanged check.
* Row identity unchanged check.
* Rendered text unchanged check.
* Runtime Lua/chunk topology unchanged check.
* `quality_state` unchanged check.
* `publish_state` unchanged check.
* Historical sealed body unchanged check.
* Diagnostic/import alias preservation check.
* Branch A/B referent-scoped current operator label residue `0` check.
* File-backed immutable surface sha256 pre/post check or explicit no-diff proof.
* Dual-zero disposition check:

```text
static_residue_gate = pass
dynamic_reach_gate = not_applicable with static-only evidence, or pass with runtime reach count 0
```

### Manual Validation

Manual validation is limited to plan/evidence review:

* Read `phase3_referent_decision.md` for branch correctness.
* Read `phase7_adversarial_review.md` for false-closeout risks.
* For Branch D, read `phase7_adversarial_review.md` to confirm the absence proof chain is complete or the blocked lane is named.
* Inspect Branch B diff if mutation or regeneration occurs.

No manual in-game QA is planned for this round.

### Validation Limits

This execution will not perform:

* Runtime rollout validation.
* Deployed closeout validation.
* Workshop packaging validation.
* Manual in-game QA pass.
* Long-session runtime validation.
* Multiplayer validation.
* External mod compatibility sweep.
* Dynamic future builder output guard beyond the confirmed referent/writer path.

---

## 8. Risk Surface Touch

### Authority Surface

Touched at governance/readpoint level. The round interprets prior closeout meaning and may update top-doc closeout state additively. It must not create a new enum mapping authority.

### Runtime Behavior Surface

None intended. Runtime Lua, chunk topology, rendered text, Browser/Wiki/Tooltip behavior, and runtime state semantics are immutable.

### Compatibility Surface

Diagnostic/import/historical `active / silent` alias compatibility must be preserved. Default current writer/validator legacy enum fail-loud behavior remains inherited from the runtime payload enum rename closeout.

### Sealed Artifact Surface

High risk if mishandled. Historical sealed decision bodies and path/hash locked evidence artifacts are read-only. Any required historical body rewrite blocks the round.

### Public-Facing Output Surface

Possible static/generated operator report output surface only. No release, deployment, Workshop, or in-game user-facing claim is in scope.

---

## 9. Risk Analysis

### Architecture Risk

* Referent recovery may be mistaken for a new mapping authority.
* Surface C may again be underdefined if the previous scan universe is copied without gap analysis.
* A deleted artifact may be misreported as cleanup success.

### Runtime Risk

* Branch B writer/recipe edits could accidentally touch runtime/source/rendered output if the wrong generator is selected.
* Runtime Lua regeneration could be triggered by a broad build command if execution scope is not constrained.

### Compatibility Risk

* Diagnostic/import/historical alias occurrences could be incorrectly treated as current operator label residue.
* Metric names such as legacy count labels could be over-normalized and break historical report interpretation.

### Regression Risk

* Generated artifact direct patch could drift from its writer and regress on next regeneration.
* VCS trace or recipe/script trace could miss renamed/deleted artifacts, producing false Branch D.
* Ambiguous candidates could lead to an overconfident Branch A.

---

## 10. Rollback Plan

Branch A/C/D with no mutation:

* Remove or archive the round-local staging root if execution must be abandoned.
* Revert append-only top-doc addenda if they were already written.
* Verify source/runtime/generated artifacts remain unchanged.

Branch B-1 direct artifact patch:

```text
git checkout -- <patched_artifact_path>
```

Then rerun invariant checks and preserve the occurrence inventory as evidence if useful.

Branch B-2 writer/recipe patch:

```text
git checkout -- <writer_or_recipe_path>
git checkout -- <generated_artifact_path>
```

Then confirm regenerated output returns to the pre-round snapshot and all source/rendered/runtime/state invariants hold.

Top-doc rollback:

* Revert only the addendum introduced by this round.
* Do not rewrite historical decision bodies.
* Ensure no leftover text claims cleanup complete for Branch C/D.

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke boundaries remain unaffected; this is Iris build/report governance only.
* Additive amendment preference for top-doc updates.
* Runtime/build-time separation must be preserved.
* Generated report/operator artifact cleanup must not expand into runtime Lua regeneration.
* Historical sealed body mutation is forbidden.
* Occurrence-level classification is required before mutation.
* Single approved mutation owner / generator path applies if Branch B opens.
* `active / silent` diagnostic/import/historical aliases remain preserved.
* Row count `2105`, row identity, rendered text, `quality_state`, `publish_state`, runtime Lua, and chunk topology are hard invariants.
* Scope expansion, undeclared authority mutation, validation bypass, silent compatibility drift, role-boundary drift, and authoritative-state drift are forbidden.
* Fail-loud over silent fallback: unrecovered referent means blocked/obsoleted closeout, not cleanup success.

---

## 12. Expected Closeout State

Expected closeout is evidence-dependent, not preselected.

Successful cleanup or no-residue closeout branches:

```text
closed_with_referent_confirmed_no_current_label_residue
closed_with_referent_confirmed_and_rewritten
closed_with_referent_confirmed_and_canonically_regenerated
```

Non-success but valid evidence closeout branch:

```text
closed_obsoleted_by_artifact_removal
```

Blocked closeout branches:

```text
blocked_missing_original_operator_artifact_referent
blocked_regeneration_recipe_missing
blocked_unknown_authority
blocked_historical_body_mutation_required
blocked_referent_input_missing
blocked_referent_ambiguous
blocked_absence_proof_incomplete
```

Branch A pass condition:

```text
referent_status = confirmed_*
current_operator_label_residue_count = 0
mutation_performed = false
referent_scoped_disposition_complete = true
cleanup_complete_claimed = false outside confirmed referent scope
```

Branch B pass condition:

```text
referent_status = confirmed_*
current_operator_label_residue_before > 0
current_operator_label_residue_after = 0
non_target_occurrence_delta = 0
invariant hash preserved
referent_scoped_disposition_complete = true
cleanup_complete_claimed = false outside confirmed referent scope
```

Branch C pass condition:

```text
referent_status = confirmed_deleted_referent
current_consumption = false
regeneration_recipe_available = false or obsolete
cleanup_complete_claimed = false
closeout = closed_obsoleted_by_artifact_removal
```

Branch D pass condition:

```text
referent_status = unrecoverable_referent_gap
4-lane absence proof completed, or blocked lane named
cleanup_complete_claimed = false
closeout = blocked_*
```

Non-decisions required in every closeout:

```text
runtime rollout = not_claimed
deployed closeout = not_claimed
Workshop release = not_claimed
manual in-game QA pass = not_claimed
ready_for_release = not_claimed
repo-wide active/silent zero = not_claimed
diagnostic/import/historical alias removal = not_claimed
```
