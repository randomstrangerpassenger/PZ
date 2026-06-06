# Iris DVF 3-3 Structural Signal Current Referent Inventory and Anchor Recovery Round Plan

> 상태: Draft v0.3-minor-review-applied
> 기준일: 2026-05-27
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP - Structural Signal Current Referent Inventory and Anchor Recovery Round` (2026-05-27 user-provided roadmap)
> review input: `REVIEW - Structural Signal Current Referent Inventory and Anchor Recovery Round (plan v0)` WARN feedback (2026-05-27), CR-1 through CR-3 and NC-1 through NC-7 incorporated in v0.2.
> review input: `REVIEW - Iris DVF 3-3 Structural Signal Current Referent Inventory and Anchor Recovery Round Plan (v0.2)` PASS-with-minor-revisions feedback (2026-05-27), NC-A through NC-E incorporated in v0.3.
> 직접 상위 readpoint:
> - 2026-04-24 `closed_with_canonical_code_path_convergence_applied`
> - 2026-04-29 `closed_with_publish_writer_authority_sealed_delta_0`
> - 2026-05-15 Frozen 2105 Baseline Reconstruction Round Branch D `blocked_reconstruction_incomplete`
> - 2026-05-20 Static Report Label Cleanup Referent Recovery Round Branch D `blocked_missing_original_operator_artifact_referent`
> - `docs/ARCHITECTURE.md` referent-recovery-first rule
> - `docs/Iris/Done/Walkthrough/iris-dvf-3-3-structural-signal-scope-split-seal-round-walkthrough.md` closeout `blocked_missing_current_readpoint_inventory`
> 계획 형식: `docs/PLAN_TEMPLATE.md`
> template attestation: this plan follows the 1-12 section structure in `docs/PLAN_TEMPLATE.md`; `docs/PLAN_TEMPLATE.md` is explicitly required by the current repository/session instructions for implementation plans and exists under `docs/`; the template is a project planning form, not semantic authority over `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, or `docs/ROADMAP.md`. Phase 0 must still verify the active template-recognition context before executing this plan; if the recognized template set has changed, execution must block or convert the plan shape before opening.
> 실행 상태: planning authority only. 이 문서는 zero-mutation observer/inventory round를 열기 위한 실행 계획이며, 작성 시점에는 runtime Lua, generated runtime artifacts, rendered text, source decisions, publish_state, quality_state, runtime_state, deployed state, release state, or closeout state를 변경하지 않는다. `DECISIONS.md`와 `ROADMAP.md` 반영은 실제 round Phase 0/Phase 7 실행 범위이며, Phase 0는 미확인 predecessor closeout을 소급 봉인하지 않고 verify-first로 처리한다.

---

## 1. Objective

이번 execution plan의 목적은 3번 리팩토링 이후 미완으로 남은 structural signal disposition을 직접 수행하는 것이 아니라, 그 disposition을 수행할 수 있는 current checkout 기준 referent / physical anchor 좌표를 확정하거나, 없음을 fail-loud 방식으로 봉인하는 것이다.

핵심 objective:

```text
current checkout 기준 structural signal occurrence/artifact inventory를 새로 측정한다
expected anchor pair를 four-lane discovery로 추적한다
expected anchor pair를 hash-level disposition enum 중 정확히 하나로 봉인한다
writer/runtime/report/preview/historical/diagnostic/test surface를 분리한다
zero-mutation invariant를 검증한다
structural disposition 자체는 닫지 않는다
```

Expected anchor pair:

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.jsonl
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.summary.json
```

Sealed identity for comparison:

```text
row sha256     = 6e84bb2f9622b79493473631d391a01c857c04ddbea869993a99856283ecb6d9
summary sha256 = 8b6b7b34ba4c5de9bf6df6d8bcdfeacc6ec86ebda9f0c0b883672177d7b508cf
source distribution sha256 = 1c8f8a3431d01f6780f8fe1a602db24ef3ae38febd936df0dec98e8fe80c41b0
section distribution sha256 = b587c663ba928bd7e6a9f8609caba9e3620c92acb6f3fa8359d868b558c0c490
overlap distribution sha256 = 831303f7134bf7d8887efed18aaa69ee373fa1ae9b19002302fbb4ad32b973fc
```

Sealed distribution for comparison only:

```text
source: BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481
section: SECTION_FUNCTION_NARROW 1433 / none 672
overlap: source_only 67 / section_only 876 / coexist 557 / dual_none 605
```

Success may claim only one of the following closeout states:

```text
closed_with_current_structural_referent_inventory_sealed
closed_with_expected_anchor_pair_superseded_by_current_artifact
closed_with_expected_anchor_pair_obsoleted_missing_referent
blocked_missing_anchor
```

Anchor disposition to closeout-state mapping:

| `anchor_disposition` | Required `closeout_state` |
|---|---|
| `recovered` | `closed_with_current_structural_referent_inventory_sealed` |
| `regenerated` | `closed_with_current_structural_referent_inventory_sealed` |
| `superseded_by_current_artifact` | `closed_with_expected_anchor_pair_superseded_by_current_artifact` |
| `obsoleted_missing_referent` | `closed_with_expected_anchor_pair_obsoleted_missing_referent` |
| `blocked_missing_anchor` | `blocked_missing_anchor` |

If `anchor_disposition` is `recovered` or `regenerated`, the closeout state must be `closed_with_current_structural_referent_inventory_sealed`, with `anchor_disposition` recorded as a separate field.

Success must not claim:

```text
structural signal disposition complete
Structural Signal Scope Split Seal Round full seal complete
FUNCTION_NARROW or ACQ_DOMINANT disposition complete
ACQ_DOMINANT remeasurement performed
publish disposition changed
runtime rollout
deployed closeout
manual in-game QA pass
Workshop readiness
ready_for_release
```

---

## 2. Scope

This round is a zero-mutation observer/inventory and anchor recovery round. It may create round-local staging artifacts, helper scripts, validation reports, review artifacts, and evidence-bound closeout docs. It must not mutate source decision bodies, runtime Lua, generated runtime chunks, rendered text, publish_state, quality_state, runtime_state, or sealed historical artifact bodies.

Round-local artifact root:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_referent_inventory_anchor_recovery_round/
```

In scope:

* Phase 0 predecessor closeout verification and round opening manifest.
* Phase 1A corpus identity pre-check before any distribution-sensitive disposition.
* Phase 1B current checkout raw occurrence inventory for these token/signature families:

```text
FUNCTION_NARROW
ACQ_DOMINANT
BODY_LACKS_ITEM_SPECIFIC_USE
LAYER4_ABSORPTION
LAYER4_ABSORPTION_CONFIRMED
SECTION_FUNCTION_NARROW
source_signal_*
section_signal_*
signal_overlap_state
dual_axis_canonical
body_plan_structural_reclassification
```

* Artifact inventory with raw path, occurrence, and artifact hints. Phase 4 is the sole final surface-disposition authority.
* Expected anchor pair discovery across four lanes:
  * current checkout exact path and filename search,
  * staging/archive/backup directory search,
  * VCS path/history trace,
  * generation recipe/script trace.
* Hash-level candidate comparison against sealed row and summary hashes.
* Single expected-anchor disposition using this enum:

```text
recovered
regenerated
superseded_by_current_artifact
obsoleted_missing_referent
blocked_missing_anchor
```

* Surface separation for writer/runtime/report/preview/historical/diagnostic/test.
* Zero-mutation invariant validation.
* Adversarial review using `docs/REVIEW_TEMPLATE.md`.
* Evidence-bound closeout and append-only top-doc updates only after gates pass.

Primary raw occurrence schema:

```json
{
  "occurrence_id": "...",
  "path": "...",
  "line_or_json_pointer": "...",
  "token": "FUNCTION_NARROW",
  "signal_family": "source_axis | section_axis | overlap_axis | legacy_single_slot | unknown",
  "artifact_kind_hint": "source | generated_report | preview | diagnostic | test | historical | runtime | writer | unknown",
  "measured_current": true,
  "sealed_historical": false,
  "surface_finalized": false,
  "notes": "..."
}
```

Primary planned deliverables:

```text
phase0_round_opening_manifest.json
phase0_predecessor_verification_report.json
phase1_corpus_identity_precheck.json
phase1_occurrence_inventory.jsonl
phase1_artifact_inventory.json
phase1_occurrence_summary.json
phase2_anchor_candidate_inventory.jsonl
phase2_anchor_discovery_report.json
phase2_lane_completion_report.json
phase3_anchor_disposition.json
phase4_surface_separation.json
artifact_referent_manifest.json
physical_referent_crosswalk.jsonl
phase5_hard_gate_report.json
immutable_surface_delta_report.json
artifact_hash_manifest.json
phase6_adversarial_review.md
phase7_closeout.json
phase7_closeout.md
```

### Explicitly Out Of Scope

* `ACQ_DOMINANT` remeasurement.
* `FUNCTION_NARROW` or `ACQ_DOMINANT` blanket isolation.
* Publish mutation or publish disposition review.
* Runtime Lua, bridge, chunk, rendered text, Browser, Wiki, or Tooltip mutation.
* Layer 3 body text rewrite.
* Layer 4 absorption revalidation.
* Frozen 2105 byte-level reconstruction.
* Complete-removal cleanup.
* `quality_baseline_v4 -> v5` cutover.
* Rendered text rebaseline.
* New enum migration.
* Repo-wide `active/silent` zero declaration.
* Deployment, Workshop, release readiness, or `ready_for_release`.

---

## 3. Non-Goals

This plan does not attempt to:

* Resolve structural signal disposition.
* Convert `FUNCTION_NARROW` or `ACQ_DOMINANT` into publish mutation candidates.
* Reopen the 2026-04-29 publish writer authority seal.
* Treat historical artifacts, Done docs, fixtures, or staging traces as current authority.
* Treat current rewrite target `0` as cleanup completion.
* Promote regenerated artifacts to current authority without deterministic input authority and output hash evidence.
* Declare that absence of a found anchor means obsolescence.
* Perform runtime validation, multiplayer validation, external mod compatibility validation, or manual in-game QA.

---

## 4. Assumptions

* `docs/Philosophy.md` is the top authority. Iris remains render-only at runtime, and runtime Lua is not a mutation surface for this round.
* `docs/DECISIONS.md` latest-date readpoint rule applies. Earlier entries remain historical trace unless superseded by later entries.
* `docs/ARCHITECTURE.md` referent-recovery-first rule applies: missing current rewrite target or occurrence target `0` is not evidence of completion.
* The predecessor `Structural Signal Scope Split Seal Round` closeout is not assumed as an immutable ledger fact until Phase 0 verifies its record. Phase 0 has three outcomes:
  * verified external record: cite the location and consume it as predecessor evidence,
  * not found: remove predecessor as a precondition and directly absorb the missing-current-readpoint problem into this round,
  * indeterminate: block this round before opening and request a separate restoration/authority input.
* Current structural read model remains `dual_axis_canonical` with `source_signal_*`, `section_signal_*`, and `signal_overlap_state`.
* Single-slot legacy structural reads are diagnostic/legacy view only.
* `FUNCTION_NARROW 7` remains preview/report structural flag only, with publish disposition delta `0`.
* `FUNCTION_NARROW` blanket isolation and `ACQ_DOMINANT` blanket isolation remain forbidden.
* `ACQ_DOMINANT` residual remeasurement remains source-expansion-gated and belongs to a separate future round.
* Historical sealed artifact hash values are comparison evidence only until a current checkout artifact is found and hash-matched or validly superseded.
* Current corpus identity may have diverged from the 2026-04-24 convergence-era corpus. Phase 1A must check current `facts/decisions/body_plan` identity, at least row-count and preferably hash-level identity, before distribution-sensitive disposition labels are considered.
* Required command/tool absence is a blocked validation result, not a pass.

---

## 5. Repository Areas Affected

### Code

None required.

Optional execution helpers may be created only if they stay within one of these planned surfaces:

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_referent_inventory_anchor_recovery_round/
Iris/build/description/v2/tools/...
Iris/build/description/v2/tests/...
```

If repo-level `tools` or `tests` files are added, the round must classify them as intentional code/test mutation and run the relevant Python validation. Such helpers must not become writer authority or runtime authority.

### Docs

```text
docs/Iris/iris-dvf-3-3-structural-signal-current-referent-inventory-anchor-recovery-round-plan.md
docs/DECISIONS.md
docs/ROADMAP.md
```

`docs/DECISIONS.md` and `docs/ROADMAP.md` are planned execution targets only for Phase 0/Phase 7. This plan file by itself does not perform the opening seal or closeout seal. Phase 0 governance wording is verify-first and must not fabricate predecessor history.

### Config

None.

### Generated Artifacts

```text
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_referent_inventory_anchor_recovery_round/
```

All generated artifacts must be new round-local evidence files. Historical sealed artifact bodies must not be rewritten.

---

## 6. Planned Changes

### Change 1 - Phase 0 Predecessor Verification and Round Opening

Purpose:

Verify whether the predecessor `Structural Signal Scope Split Seal Round` closeout `blocked_missing_current_readpoint_inventory` exists as an actual record before this round consumes it. Phase 0 must not retroactively invent or seal an unverified predecessor fact.

Files:

```text
phase0_predecessor_verification_report.json
docs/DECISIONS.md
Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_referent_inventory_anchor_recovery_round/phase0_round_opening_manifest.json
```

Implementation Notes:

* Search for the predecessor closeout in current governance docs, Done walkthroughs, staging artifacts, and relevant VCS trace.
* Record one Phase 0 verification branch:

```text
verified_external_record
predecessor_not_found_absorbed_by_this_round
blocked_predecessor_record_indeterminate
```

* `verified_external_record`: cite the exact path/heading/hash or VCS evidence. A `DECISIONS.md` addendum may state that this round consumes that verified record, but must not pretend the fact was previously sealed in `DECISIONS.md`.
* `verified_external_record` minimum evidence:
  * A current `docs/DECISIONS.md` / `docs/ROADMAP.md` / `docs/ARCHITECTURE.md` entry that names the predecessor closeout is sufficient, or
  * a VCS commit/path trace or round-local staging artifact that records the predecessor closeout is sufficient, or
  * a Done walkthrough alone is not sufficient as authority; it must be corroborated by at least one VCS trace, staging artifact, top-doc pointer, or hash-bearing closeout artifact.
* When a Done walkthrough contributes to `verified_external_record`, closeout wording must say this round consumes a verified provenance record. It must not say the predecessor was already sealed in `DECISIONS.md` unless a `DECISIONS.md` entry actually exists.
* `predecessor_not_found_absorbed_by_this_round`: remove the predecessor as an opening precondition and state that this round directly absorbs the missing-current-readpoint problem, following the 2026-05-27 absorption precedent.
* `blocked_predecessor_record_indeterminate`: do not open the round. Emit a blocked pre-opening report and request restoration or authoritative input.
* Verify `docs/PLAN_TEMPLATE.md` is still the recognized implementation-plan template for this session or governance context. If not, use `blocked_template_recognition_indeterminate` until the plan is converted or the template is recognized.
* Opening manifest must include execution scale, mutable and immutable surfaces, authority read order, closeout branches, forbidden actions, and closeout ceiling.
* Closeout ceiling must stay at `readpoint/inventory seal`.
* Runtime/publish/quality mutation authorization must be absent.

Validation:

* Confirm the Phase 0 branch is recorded before Phase 1A starts.
* Confirm no `DECISIONS.md` wording asserts an unverified predecessor as a historical sealed fact.
* Confirm `verified_external_record` is not based on an uncorroborated Done walkthrough.
* Confirm template recognition status is recorded.
* Confirm latest `DECISIONS.md` entries, if written, do not contradict latest-readpoint rule.
* Confirm forbidden actions include `ACQ_DOMINANT` remeasurement, blanket isolation, runtime mutation, publish mutation, and structural disposition closeout.
* Confirm Phase 1A is allowed only for `verified_external_record` or `predecessor_not_found_absorbed_by_this_round`.

---

### Change 2 - Phase 1A Corpus Identity Pre-Check

Purpose:

Determine whether the current input corpus is identical to, diverged from, or indeterminate relative to the 2026-04-24 convergence-era corpus before distribution-sensitive anchor disposition.

Files:

```text
phase1_corpus_identity_precheck.json
```

Implementation Notes:

* Check current `facts/decisions/body_plan` inputs used by the structural observer path.
* Compare against convergence-era corpus identity where hash or manifest evidence exists.
* At minimum record:

```json
{
  "corpus_identity_state": "identical | diverged | indeterminate",
  "current_row_count": 2105,
  "expected_row_count": 2105,
  "row_count_2105_match": true,
  "hash_comparison_available": true,
  "hash_comparison_result": "match | mismatch | not_available",
  "disposition_branch_constraints": ["..."]
}
```

* If `corpus_identity_state = diverged`, `recovered` and `regenerated` are automatically excluded as current disposition labels. Distribution deltas must be reported as current measurement deltas, not anchor failure by themselves.
* If `corpus_identity_state = indeterminate`, Phase 3 must either block with sub-label `blocked_corpus_identity_indeterminate` under `blocked_missing_anchor`, or justify why an exact current-authority hash match is still sufficient.
* Row-count `2105` mismatch is a hard warning that the old anchor name cannot be assumed to describe current corpus shape.

Validation:

* Record input paths, hashes if available, row-count, and comparison source.
* Confirm Phase 3 reads `corpus_identity_state` before allowing `recovered` or `regenerated`.
* Confirm sealed 2026-04-24 distributions remain comparison-only when the corpus diverged.

---

### Change 3 - Phase 1B Current Raw Occurrence and Artifact Inventory

Purpose:

Measure structural signal occurrences and artifact referents from current checkout only, without inheriting historical counts as current truth. Phase 1B records raw occurrence data and preliminary artifact hints; Phase 4 owns final surface disposition.

Files:

```text
phase1_occurrence_inventory.jsonl
phase1_artifact_inventory.json
phase1_occurrence_summary.json
```

Implementation Notes:

* Scan the token/signature list in Section 2.
* Record every occurrence with token family, path, line or JSON pointer, raw artifact kind hint, measured/current status, and historical marker.
* Do not make Phase 1B the final authority for current/provenance/diagnostic/test/runtime/writer classification.
* Keep `measured_current` and `sealed_historical` separate.
* `ACQ_DOMINANT` occurrences are inventory facts only, not remeasurement input.
* Historical Done docs, tests, diagnostic fixtures, and staging traces must not be counted as current authority by default.

Validation:

* Occurrence count must equal recorded raw occurrence rows.
* `unknown` count must be `0` or each unknown must have explicit blocked disposition.
* Compare current measured counts against sealed 2026-04-24 distributions as a factual comparison only. Do not force equality.
* Confirm no source/runtime/rendered/state mutation occurred.

---

### Change 4 - Phase 2 Four-Lane Expected Anchor Pair Discovery

Purpose:

Recover, supersede, or fail-loud on the expected anchor pair using complete discovery evidence.

Files:

```text
phase2_anchor_candidate_inventory.jsonl
phase2_anchor_discovery_report.json
phase2_lane_completion_report.json
```

Implementation Notes:

* Lane A current checkout search:
  * exact expected path check,
  * filename search for `body_plan_structural_reclassification.2105.jsonl` and `.summary.json`,
  * content search for `body_plan_structural_reclassification` and structural signal fields.
* Lane B staging/archive/backup search:
  * minimum roots: `Iris/build/description/v2/staging/`, `docs/Iris/Done/`, `docs/Iris/Done/Walkthrough/`, `docs/Archived/`,
  * any repo-local path matching archive/backup/staging naming discovered by file search,
  * all searched roots and exclusions recorded.
* Lane C VCS trace:
  * path trace for both expected anchor files,
  * filename/content trace where path trace fails,
  * commit count and last-seen refs recorded,
  * any unavailable VCS operation recorded as blocked evidence, not ignored.
* Lane D generation recipe/script trace:
  * search current build/report scripts for the artifact name and dual-axis field names,
  * identify whether a deterministic recipe exists,
  * record whether the recipe targets sealed hashes, current corpus output, diagnostic output, or no longer exists.
* Track row artifact and summary artifact independently to avoid hiding half-present states.
* Compute sha256 for every candidate and compare against sealed row and summary hashes.
* Record per-lane candidate counts and completion status.
* Record `absence_proof_completed = true` only when all four lanes have explicit completion evidence.
* Half-present pair states must use explicit sub-labels:

```text
half_present_row_only
half_present_summary_only
half_present_hash_mismatch
half_present_authority_mismatch
```

Validation:

* Every expected anchor must have `found`, `not_found`, or `candidate` status.
* Every candidate must have path, lane, role, sha256, and authority status.
* Every lane must have `search_scope`, `candidate_count`, `completion_status`, and `completion_evidence`.
* Any half-present pair must be explicit in the discovery report.
* Historical artifacts may be provenance only unless they satisfy current authority criteria.

---

### Change 5 - Phase 3 Hash-Level Anchor Disposition

Purpose:

Choose exactly one expected-anchor disposition and verify the label preconditions.

Files:

```text
phase3_anchor_disposition.json
```

Implementation Notes:

Disposition rules:

| Label | Required precondition |
|---|---|
| `recovered` | Current artifact row and summary hashes exactly match sealed row and summary hashes, current authority status is proven, and corpus identity does not exclude recovery. Path match alone is insufficient. |
| `regenerated` | Narrow label only: deterministic procedure reproduces the sealed row and summary hashes exactly from verified same-corpus authority input. Distribution-only reproduction is insufficient. If output hash differs, use another label. |
| `superseded_by_current_artifact` | A current same-role artifact exists, is compatible with the current dual-axis read model, and a crosswalk proves it replaces the expected anchor role. Distribution is comparison-only; equality is not required. Distribution delta is recorded as `accepted_delta` or `current_measurement_delta`. |
| `obsoleted_missing_referent` | Four-lane absence proof is complete, no current replacement artifact is selected, positive proof shows the old anchor is historical/provenance/diagnostic/non-current, and current writer/runtime/report validators do not depend on it. Non-dependency proof is required. |
| `blocked_missing_anchor` | Four-lane discovery is complete, but no positive current referent, no valid current same-role replacement, and no sufficient non-current/non-dependency proof exists. `absence_proof_completed = true` is required. |

Bounded non-dependency proof surface for `obsoleted_missing_referent`:

```text
Iris/build/description/v2/tools/build/ structural observer/report/compose scripts
Iris/build/description/v2/tools/ validators or helper scripts that reference structural readpoints
Iris/build/description/v2/tests/ tests that reference structural signal or body_plan_structural_reclassification artifacts
Iris/build/description/v2/staging/compose_contract_migration/ current round and current structural staging manifests
Iris/Iris/media/lua/ packaged runtime data and manifest paths, reference-scan only
docs/DECISIONS.md, docs/ARCHITECTURE.md, docs/ROADMAP.md current readpoint entries, pointer-scan only
```

This proof is a bounded path/import/reference scan plus recipe trace over the listed surfaces. It is not a repo-wide metaphysical proof of non-use. Historical docs and Done walkthroughs may prove provenance, but they do not count as current writer/runtime/report dependency by themselves.

Hard guards:

```text
recovered requires exact hash match
regenerated requires exact sealed hash reproduction
corpus divergence excludes recovered/regenerated
superseded_by_current_artifact does not require distribution equality
obsoleted_missing_referent requires non-current proof and non-dependency proof
terminal absence labels require absence_proof_completed = true
```

Validation:

* Automatic precondition check must reject invalid label selection.
* `corpus_identity_state = diverged` must reject `recovered` and `regenerated`.
* `absence_proof_completed = false` must reject `obsoleted_missing_referent` and `blocked_missing_anchor`.
* `superseded_by_current_artifact` must include old-role to current-artifact crosswalk and record distribution delta as comparison-only.
* `obsoleted_missing_referent` must include non-current proof and bounded non-dependency proof over the listed surfaces. A replacement artifact moves the branch to `superseded_by_current_artifact`, not `obsoleted_missing_referent`.
* `blocked_missing_anchor` may carry sub-labels such as `blocked_corpus_identity_indeterminate`, `half_present_row_only`, `half_present_summary_only`, or `blocked_absence_proof_incomplete` if evidence requires.

---

### Change 6 - Phase 4 Surface Separation

Purpose:

Connect occurrences to physical artifact referents and separate current writer/runtime/report/preview/historical/diagnostic/test surfaces.

Files:

```text
phase4_surface_separation.json
artifact_referent_manifest.json
physical_referent_crosswalk.jsonl
```

Implementation Notes:

* Phase 4 is the single authority for final surface separation. Phase 1B raw artifact hints are inputs only.
* Every occurrence must map to exactly one primary surface.
* Current authority artifacts must have hash entries.
* Rejected artifacts must include rejection reason.
* Legacy single-slot report paths must be diagnostic/compat only.
* Report and preview surfaces are read-only observers and do not reopen 2026-04-29 publish disposition.

Validation:

* Surface classes must not contradict `dual_axis_canonical`.
* Diagnostic, historical, and test surfaces must not become writer authority.
* Report and preview surfaces must declare read-only status.
* `FUNCTION_NARROW 7` remains preview/report structural flag only.

---

### Change 7 - Phase 5 Hard Gate and Invariant Validation

Purpose:

Prove the round remained an immutable/current-authority zero-mutation readpoint/inventory round while allowing round-local artifacts, optional helpers/tests, and governed addenda to be created.

Files:

```text
phase5_hard_gate_report.json
immutable_surface_delta_report.json
artifact_hash_manifest.json
```

Implementation Notes:

Record these state fields:

```text
round_local_artifact_created = true
helper_or_test_code_changed = true/false
governance_addendum_written = true/false
template_recognition_status = recognized | converted | blocked_template_recognition_indeterminate
```

Validate these must-be-false invariants:

```text
immutable_surface_mutation_performed = false
runtime_mutation_performed = false
source_decision_mutation_performed = false
facts_mutation_performed = false
rendered_text_mutation_performed = false
publish_quality_state_mutation_performed = false
runtime_state_mutation_performed = false
browser_wiki_tooltip_consumer_mutation_performed = false
ACQ_DOMINANT remeasurement not run
blanket isolation not reopened
historical_body_mutation_performed = false
```

Gate states:

```text
static_residue_gate = not_applicable
static_residue_gate_reason = no cleanup/rewrite target is selected in this inventory round
dynamic_reach_gate = not_applicable
dynamic_reach_gate_reason = no runtime/deployed behavior is executed or mutated
invariant_gate = pass
```

Validation:

* Use `git diff --stat` and `git diff` to classify touched surfaces.
* Only round-local staging artifacts, approved helper/test files, and planned doc addenda may be dirty.
* Run Python validation if helper/test code is added or if the execution harness changes.
* Lua syntax validation is `not_applicable` unless Lua files are touched; if Lua is touched accidentally, the round fails its immutable-surface gate before relying on syntax pass.

---

### Change 8 - Phase 6 Adversarial Review

Purpose:

Review the plan outputs against `docs/REVIEW_TEMPLATE.md`, focusing on false recovery, false obsolescence, scope drift, and overclaiming.

Files:

```text
phase6_adversarial_review.md
```

Implementation Notes:

* Review must be a separate adversarial pass after artifacts and draft closeout are frozen. The review report must record whether it was performed in a separate session/pass and by whom or by what review context.
* Review must explicitly check C1 false `recovered` risk.
* Review must explicitly check C2 false `obsoleted_missing_referent` risk.
* Review must check corpus identity branch handling and lane completion evidence.
* Review must verify `inventory sealed` is not worded as `structural disposition solved`.
* Review must verify validation ceiling and non-claims.

Validation:

```text
blocker count = 0
major count = 0
```

Phase 7 must not start if blocker or major findings remain unresolved.

---

### Change 9 - Phase 7 Closeout and Trace Addenda

Purpose:

Close the round with evidence-bound claims and update governance docs without expanding the claim beyond the artifacts.

Files:

```text
phase7_closeout.json
phase7_closeout.md
docs/DECISIONS.md
docs/ROADMAP.md
```

Implementation Notes:

* Select exactly one closeout state from Section 1.
* Record the Phase 0 predecessor verification branch. If the predecessor was absent, closeout wording must say this round absorbed the missing-current-readpoint problem directly and must not claim a past predecessor seal.
* Record current structural signal readpoint manifest.
* Record expected anchor pair disposition.
* Record the disposition to closeout-state mapping result from Section 12.
* Record corpus identity state and whether it excluded `recovered` / `regenerated`.
* Record template recognition status.
* Record non-claims and next-round eligibility.
* Do not automatically open a follow-up round.

Mandatory closeout sentences:

```text
This round does not perform ACQ_DOMINANT remeasurement.
This round does not reopen FUNCTION_NARROW or ACQ_DOMINANT blanket isolation.
This round does not mutate publish_state, quality_state, rendered text, runtime Lua, or deployed runtime.
This round does not declare release readiness, Workshop readiness, deployed closeout, or ready_for_release.
This round does not close structural signal disposition.
```

Validation:

* Every closeout claim must map to an evidence artifact.
* `anchor_disposition` and `closeout_state` must match the mapping table.
* Non-claims must be present.
* If `blocked_missing_anchor`, the closeout must state attempted recovery paths and whether next valid round is restoration or authoritative reconstruction.
* `docs/DECISIONS.md` and `docs/ROADMAP.md` changes must be additive and evidence-bound. Governance addenda are current statements or supersession records, not rollbackable historical rewrites.

---

## 7. Validation Plan

### Automated Validation

Planned commands and checks:

```powershell
git diff --stat
git diff
```

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

The Python test command is required if execution adds or modifies Python helpers/tests, validator logic, or current build tooling. If Python is unavailable, validation is blocked, not passed.

JSON validation:

```powershell
jq empty <generated-json-files>
```

If `jq` is unavailable, JSON validation must be performed by an equivalent explicitly recorded parser command. Missing parser support is blocked, not passed.

Hash validation:

```text
corpus identity pre-check against convergence-era evidence where available
row-count 2105 check
sha256 for each deliverable
sha256 candidate comparison against sealed expected row/summary hashes
sha256 manifest for accepted current authority artifacts
per-lane candidate count and completion evidence for absence_proof_completed
```

Lua syntax validation:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Lua syntax validation is required only if Lua files are touched. In the intended zero-Lua-mutation path it is explicitly `not_applicable`.

### Manual Validation

* Inspect `phase3_anchor_disposition.json` against the disposition precondition table.
* Inspect `phase1_corpus_identity_precheck.json` before accepting any distribution-sensitive disposition.
* Inspect `phase2_lane_completion_report.json` before accepting `absence_proof_completed = true`.
* Inspect `phase3_anchor_disposition.json` for bounded non-dependency proof if `anchor_disposition = obsoleted_missing_referent`.
* Inspect closeout JSON for disposition to closeout-state mapping.
* Inspect `phase4_surface_separation.json` for exactly-one primary surface per occurrence.
* Inspect closeout wording for forbidden claims.
* Inspect Phase 0 template recognition status.
* Run adversarial review using `docs/REVIEW_TEMPLATE.md`.

### Validation Limits

* No runtime validation.
* No multiplayer validation.
* No deployment validation.
* No manual in-game QA.
* No external mod compatibility sweep.
* No `ACQ_DOMINANT` remeasurement.
* No publish disposition re-evaluation.
* No release readiness or Workshop readiness validation.

---

## 8. Risk Surface Touch

### Authority Surface

No writer/observer authority is reassigned by this plan. The round only inventories and disposes the current existence/status of the expected structural signal readpoint anchor. Any authority wording in Phase 7 must be evidence-bound to the selected anchor disposition.

### Runtime Behavior Surface

None. Runtime Lua, bridge files, generated chunks, deployed runtime, and rendered text are immutable for this round.

### Compatibility Surface

None expected. The round creates inventory and governance artifacts only. It must not change Browser/Wiki/Tooltip behavior, external mod input contracts, resolver behavior, or runtime payload contracts.

### Sealed Artifact Surface

Read-only. Sealed historical artifact hashes may be compared but sealed artifact bodies, fixtures, staging artifact bodies, and Done walkthroughs must not be rewritten.

### Public-Facing Output Surface

None. This round does not change user-facing copy, UI behavior, tooltip behavior, Browser behavior, Wiki behavior, release packaging, or Workshop state.

---

## 9. Risk Analysis

### Architecture Risk

* False recovery: a similar artifact could be labeled `recovered` without exact hash match. The plan blocks this by requiring row and summary hash equality.
* Corpus category error: a changed input corpus could be mistaken for missing anchor evidence. Phase 1A requires corpus identity pre-check before Phase 3 disposition.
* False obsolescence: a missing anchor could be labeled `obsoleted_missing_referent` without non-current proof and non-dependency proof. The plan blocks this by requiring both proofs plus complete absence proof.
* False supersession: a current same-role artifact could be rejected only because its distribution differs from the sealed distribution. The plan treats distribution equality as comparison-only and records accepted/current measurement deltas.
* Historical authority drift: Done docs, staging artifacts, or diagnostic fixtures could be accidentally promoted to current authority. Phase 1B records raw hints only; Phase 4 owns final surface classification and rejection reasons.
* Legacy single-slot drift: old reports could be read as dual-axis canonical authority. Phase 4 must classify them diagnostic/compat only unless current dual-axis criteria are satisfied.

### Runtime Risk

* Runtime mutation would violate round scope. Phase 5 treats runtime Lua/chunk/rendered/state deltas as invariant failures.
* Accidental Lua edits must fail the immutable-surface gate even if syntax validation passes.

### Compatibility Risk

* Reopening `ACQ_DOMINANT` or blanket isolation would cross into a different future round. Phase 0 and Phase 5 explicitly forbid and validate against this drift.
* Treating report/preview classification as publish disposition could disturb the 2026-04-29 seal. Phase 4 declares report/preview read-only observer status.

### Regression Risk

* Inventory scripts could miss files or scan too narrowly. Phase 2 requires four-lane discovery, records search scope, and records candidate counts per lane.
* Half-present anchor pair could be hidden by a single disposition label. Phase 2 tracks row and summary independently.
* Validation could overclaim if command tools are missing. Missing required validation tools must be reported as blocked.
* Closeout could claim structural disposition completion. Phase 6 and Phase 7 explicitly reject that wording.

---

## 10. Rollback Plan

This is planned as a zero-mutation round for immutable/current authority surfaces. Rollback should normally be limited to round-local staging artifacts, helper scripts, validator/test scripts, and closeout drafts created by the execution. Governance-ledger writes in `docs/DECISIONS.md` or `docs/ROADMAP.md` are not clean rollback targets after publication; they must be superseded by later additive correction entries under the latest-readpoint rule.

Rollback steps:

1. Review touched surfaces with `git diff --stat` and `git diff`.
2. If source decisions, facts, rendered text, runtime Lua/chunks, publish_state, quality_state, or runtime_state changed, treat the round as failed and revert those unauthorized changes.
3. Preserve or remove round-local staging artifacts according to whether they remain useful as failed-attempt evidence.
4. If a validator/test encodes an invalid premise, remove it or downgrade it to diagnostic-only in a follow-up corrective patch.
5. If closeout text overclaims after governance publication, supersede it with an additive correction entry under the latest-readpoint rule.
6. If expected anchor pair was wrongly marked `obsoleted_missing_referent`, supersede the closeout with `blocked_missing_anchor` unless non-current proof and non-dependency proof are produced.

Rollback must not rewrite sealed historical artifact bodies. If a sealed historical body was modified, the round fails its immutable-surface invariant.

---

## 11. Governance Constraints

* `docs/Philosophy.md` remains the top authority.
* Iris runtime remains render-only.
* Hub & Spoke and module boundary rules remain untouched.
* Single-writer authority is not reassigned.
* `docs/DECISIONS.md` latest-date readpoint rule controls any correction or supersession.
* Additive-only treatment applies to sealed artifacts and governance history.
* Phase 0 predecessor handling is verify-first. Unverified predecessor history must not be sealed retroactively.
* Historical artifacts, Done docs, fixtures, and staging traces are provenance unless current authority criteria are explicitly satisfied.
* `referent-recovery-first` applies before cleanup/disposition claims.
* Hash-level immutability applies to sealed artifact comparison.
* `FUNCTION_NARROW` and `ACQ_DOMINANT` blanket isolation remain forbidden.
* `ACQ_DOMINANT` remeasurement remains forbidden in this round.
* 2026-04-29 publish writer authority seal remains intact.
* Failure must be fail-loud, not silent absence-to-obsolete conversion.
* No deployed closeout, release readiness, Workshop readiness, or `ready_for_release` claim is allowed.

---

## 12. Expected Closeout State

Expected closeout target after execution is exactly one of:

```text
closed_with_current_structural_referent_inventory_sealed
closed_with_expected_anchor_pair_superseded_by_current_artifact
closed_with_expected_anchor_pair_obsoleted_missing_referent
blocked_missing_anchor
```

Disposition to closeout mapping:

| `anchor_disposition` | `closeout_state` |
|---|---|
| `recovered` | `closed_with_current_structural_referent_inventory_sealed` |
| `regenerated` | `closed_with_current_structural_referent_inventory_sealed` |
| `superseded_by_current_artifact` | `closed_with_expected_anchor_pair_superseded_by_current_artifact` |
| `obsoleted_missing_referent` | `closed_with_expected_anchor_pair_obsoleted_missing_referent` |
| `blocked_missing_anchor` | `blocked_missing_anchor` |

The closeout JSON must carry both `anchor_disposition` and `closeout_state`. The closeout state alone is not allowed to hide whether the current referent was `recovered` or `regenerated`.

Pre-opening Phase 0 branch handling:

```text
verified_external_record -> round may proceed and cite predecessor evidence
predecessor_not_found_absorbed_by_this_round -> round may proceed without predecessor precondition
blocked_predecessor_record_indeterminate -> round does not open; blocked pre-opening report only
```

`blocked_missing_anchor` is an acceptable blocked closeout, not a failed execution, if and only if:

```text
four-lane discovery completed
absence_proof_completed = true
corpus identity branch recorded
no positive current referent was recovered
no valid current same-role replacement exists
no sufficient non-current/non-dependency proof exists for obsoleted_missing_referent
the closeout states why the missing anchor is required
the closeout records every attempted recovery path
the closeout names the next valid path as restoration or authoritative reconstruction
```

If the pair is half-present, the final branch must carry one of these sub-labels:

```text
half_present_row_only
half_present_summary_only
half_present_hash_mismatch
half_present_authority_mismatch
```

If corpus identity is indeterminate and prevents disposition, `blocked_missing_anchor` must carry sub-label `blocked_corpus_identity_indeterminate`.

No closeout branch may declare structural signal disposition complete. This round can only seal the current readpoint inventory/anchor disposition that a later structural disposition round may consume.
