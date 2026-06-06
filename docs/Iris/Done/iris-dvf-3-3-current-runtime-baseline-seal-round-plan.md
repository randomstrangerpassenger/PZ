# Iris DVF 3-3 Current Runtime Baseline Seal Round Plan

> 상태: Draft v0.3-plan  
> 기준일: 2026-05-23  
> 상위 기준: `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`  
> authority input: `ROADMAP - Iris DVF 3-3 Current Runtime Baseline Seal Round (Consolidated)` (2026-05-22 user-provided synthesis)  
> review input: `REVIEW - Iris DVF 3-3 Current Runtime Baseline Seal Round Plan (Consolidated)` WARN feedback (2026-05-23), C1, I1 through I4, and M1 through M5 incorporated in v0.2.  
> review input: `REVIEW (v2 Re-Review) - Iris DVF 3-3 Current Runtime Baseline Seal Round Plan (Consolidated)` WARN feedback (2026-05-23), helper/output-surface conflict and M2 through M6 incorporated in v0.3.  
> 기존 문제 매핑: `Manual In-Game Validation QA Round` Phase 1 identity pre-gate blocker  
> 계획 형식: implementation plan 1-12 section structure. This planning form is not semantic authority over `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, or `ROADMAP.md`.  
> phase mapping note: this plan maps the ROADMAP Phase 0 through Phase 8 flow to Change 1 through Change 9 one-to-one; no extra execution phase is introduced beyond the ROADMAP flow.  
> 실행 상태: planning authority only. 이 문서는 read-only current runtime baseline seal round를 열기 위한 실행 계획이며, 작성 시점에는 runtime Lua, chunk files, rendered text, source decisions, publish decisions, deployed state, release state, or top-doc closeout state를 변경하지 않는다.

---

## 1. Objective

이번 execution plan의 목적은 MIGV-QA Phase 1을 재개하기 전에 current checkout의 DVF 3-3 deployable runtime chunks 자체를 새 sealed runtime baseline으로 봉인하는 것이다.

핵심 objective:

```text
current checkout deployable runtime authority must be measured directly
IrisLayer3DataChunks.lua + Chunk001..011.lua must become the sealed identity referent
row inventory, payload inventory, consumer filtering contract, and file hashes must be sealed
historical staged hash 0390272b... remains historical readpoint only
MIGV-QA Phase 1 must reference the new sealed current-runtime evidence path/hash
```

이번 round의 검증 질문은 다음 하나로 제한한다.

```text
현재 checkout의 chunk deployable runtime payload가 MIGV-QA Phase 1이 참조할 수 있는
sealed baseline evidence로 충분히 봉인되었는가?
```

성공 시 최대 선언 가능 범위:

```text
sealed_current_runtime_baseline_for_MIGV_QA_Phase_1
```

성공해도 선언 금지:

```text
manual in-game validation pass
deployed closeout
runtime rollout
release readiness
Workshop readiness
tooltip validation
full runtime equivalence
frozen 2105 byte-level reconstruction
historical staged hash parity recovery
```

Required handoff sentence:

```text
MIGV-QA Phase 1 identity pre-gate must use the sealed current runtime baseline
from DVF 3-3 Current Runtime Baseline Seal Round, not the historical staged hash.
```

---

## 2. Scope

This round is a read-only authority/evidence seal. It scans current deployable runtime files, writes round-local evidence artifacts, classifies the baseline, and hands a single sealed evidence path/hash to MIGV-QA Phase 1.

In scope:

* Scope lock and pre-gate for `DVF 3-3 Current Runtime Baseline Seal Round`.
* Round-local artifact root:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/
```

* Authoritative input file set:

```text
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk001.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk002.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk003.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk004.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk005.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk006.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk007.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk008.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk009.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk010.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk011.lua
```

* Logical deployable referent to reconcile with current governance documents:

```text
Iris/Data/IrisLayer3DataChunks.lua
Iris/Data/IrisLayer3DataChunks/Chunk001..011.lua
```

Phase 0 must seal that the physical workspace paths above are the same PZ deployable target represented by the logical `Iris/Data/...` paths in `ARCHITECTURE.md` and `DECISIONS.md`.

* Explicit non-authority check:

```text
Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua
```

This monolith is not deployable runtime authority. Its current status must be recorded as absent, present-non-authority, or present-auto-load-risk.

* Current file identity scan:

```text
manifest existence and sha256
manifest chunk reference parsing
Chunk001..011 existence and sha256
filesystem chunk count
missing / extra chunk inventory
monolith status and active deployable path risk
historical hash mismatch note
```

* Current payload inventory scan:

```text
total row count
per-chunk row count
runtime identity key inventory
duplicate identity key inventory
adopted / unadopted split
legacy active / silent residue inventory
quality_state split
publish_state split
missing / null / unknown publish_state inventory
text_ko missing / nil / empty / whitespace-only inventory
malformed row inventory
```

* Consumer filtering contract scan:

```text
layer3 renderer chunk manifest load path
monolith fallback reachability
Browser default filtering
Wiki default filtering
Tooltip static contract only
internal_only retention and default suppression
missing publish_state behavior
nil text_ko behavior
legacy enum dependency
publish decision ownership
```

* Negative invariant and fail-loud verification:

```text
runtime artifacts unchanged
row identity unchanged
rendered text unchanged
quality_state unchanged
publish_state unchanged
source decisions unchanged
chunk topology unchanged
round directory is the only output surface
all deltas classified as match or finding
row-count/source-split current-readpoint deltas reconciled or blocked
```

* Validation with the existing project commands:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

* Adversarial review using `REVIEW_TEMPLATE.md`.
* Closeout and MIGV-QA Phase 1 handoff.
* Optional additive top-doc addendum after closeout only.

### Explicitly Out Of Scope

* Runtime Lua mutation.
* Chunk regeneration.
* Re-chunking.
* Lua bridge regeneration.
* Rendered text rebaseline.
* Source decision mutation.
* `publish_state`, `quality_state`, `source`, or `text_ko` mutation.
* Missing `publish_state` auto-fill.
* Nil or empty `text_ko` auto-repair.
* Legacy `active / silent` automatic rewrite.
* `internal_only` row deletion.
* `unadopted` row deletion.
* Monolith restoration.
* Monolith promotion to deployable authority.
* Frozen 2105 byte-level baseline recovery.
* Historical staged hash parity recovery.
* Manual in-game validation.
* Deployed closeout.
* Runtime rollout.
* Release readiness or Workshop readiness.
* Tooltip implementation or tooltip validation.
* B42 porting.
* External mod compatibility sweep.

---

## 3. Non-Goals

This plan does not attempt to:

* Prove that current chunks are byte-identical to the historical staged hash `0390272b...`.
* Treat `2105 / 2084 / 21` as an input assumption.
* Convert inventory findings into cleanup work inside this round.
* Decide whether missing `publish_state` or nil `text_ko` should be fixed.
* Reopen sealed chunk topology, monolith non-authority, or enum decision bodies.
* Reclassify `adopted / unadopted`, `quality_state`, or `publish_state`.
* Change Browser, Wiki, Tooltip, or renderer behavior.
* Make Browser/Wiki consumers publish writers.
* Run manual in-game validation.
* Claim that finding-free inventory means release readiness.
* Claim that `sealed_with_inventory_findings` means no defects exist.

---

## 4. Assumptions

Authority assumptions:

* `Philosophy.md` is the top authority.
* Iris remains render-only at runtime and must not generate interpretation, recommendation, or comparison.
* `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md` are current ecosystem readpoints.
* Existing sealed decisions remain intact:

```text
chunk manifest + chunk files are Layer 3 deployable runtime authority
monolith IrisLayer3Data.lua is not deployable runtime authority
11 chunk topology is sealed
monolith require fallback is not opened
layer3_renderer.lua defaults to chunk-manifest source
canonical payload enum is adopted / unadopted
legacy active / silent is diagnostic/import/historical alias only
internal_only means default consumer visibility suppression, not runtime deletion
adopted means runtime-adopted, not quality-pass
unadopted does not mean publish_state or deletion
```

Input assumptions:

* The only primary runtime authority input is the current workspace file set listed in Section 2.
* Historical staged/static artifact hash `0390272b...` is comparison-only.
* Prior readpoint counts such as `2105 / 2084 / 21` are not hardcoded parser inputs.
* If current measured counts differ from `ARCHITECTURE.md` and `DECISIONS.md` current readpoints that state `2105 / 2084 / 21`, this round must close as `blocked_current_readpoint_reconciliation_required`.
* Current readpoint reconciliation is a separate follow-up round, not a same-round addendum, and is not frozen 2105 byte-level reconstruction.

Implementation assumptions:

* The round writes only under:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/
```

* Runtime chunks, manifest, source decisions, rendered artifacts, consumer code, and top-level sealed decision bodies remain immutable during scanning.
* No new helper script or code file is allowed in this round. Use existing tooling, one-off local commands, or already-existing scripts only.
* `round_directory_only_output = true` remains strict: the only planned outputs are round-local generated evidence artifacts and allowed closeout markdown/json under the round directory.
* Structured parsing is preferred over ad hoc string matching where existing repository tooling or read-only local commands can provide it.

Validation assumptions:

* Python validation may be claimed only when the exact unittest command exits `0`.
* Lua syntax validation may be claimed only when the exact syntax command exits `0`.
* Missing required tooling is a blocked validation result, not a pass.
* Consumer behavior classified as `undefined` for missing `publish_state` or nil `text_ko` blocks the baseline seal as `blocked_contract_undefined`.
* Consumer behavior classified as `crash`, `hard_error`, or current-runtime `fail_loud` blocks the seal as `blocked_contract_runtime_breakage` when the corresponding inventory count is greater than `0`.

---

## 5. Repository Areas Affected

### Code

None planned for runtime or consumer code.

Read-only inspection targets:

```text
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua
Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua
Iris/media/lua/client/Iris/**
Iris/build/description/v2/tools/**
Iris/build/description/v2/tests/**
tools/check_lua_syntax.ps1
```

No new helper script is allowed in this round. If existing tooling is insufficient, use one-off local read-only commands or close the round as blocked rather than adding code.

### Docs

This plan document:

```text
docs/Iris/iris-dvf-3-3-current-runtime-baseline-seal-round-plan.md
```

Optional additive closeout/readpoint addenda after closeout:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Historical decision bodies must not be rewritten.

### Config

None planned.

### Generated Artifacts

Primary round-local artifacts:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_hash_manifest.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_chunk_identity_report.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_payload_inventory.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_consumer_filtering_contract_report.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_consumer_filtering_contract_summary.md
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/missing_publish_state_inventory.jsonl
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/nil_text_ko_inventory.jsonl
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/legacy_enum_residue_inventory.jsonl
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/duplicate_runtime_key_inventory.jsonl
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/closeout/current_runtime_baseline_seal_closeout.md
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/closeout/current_runtime_baseline_seal.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/closeout/migv_qa_phase1_handoff.md
```

Additional phase artifacts:

```text
phase0_scope_lock.json
phase0_immutable_hash_snapshot.json
phase4_negative_invariant_report.json
phase5_hard_gate_report.json
phase7_adversarial_review.md
```

---

## 6. Planned Changes

### Change 1 - Phase 0 scope lock and pre-gate

Purpose:

Seal the read-only boundary, authoritative input paths, non-authority paths, mutable output surface, immutable surfaces, closeout ceiling, and non-claim list before any scan begins.

Files:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/phase0_scope_lock.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/phase0_immutable_hash_snapshot.json
```

Implementation Notes:

* Record round name:

```text
DVF 3-3 Current Runtime Baseline Seal Round
```

* Declare execution scale:

```text
authority/evidence seal
runtime artifact mutation = forbidden
```

* Declare authoritative input:

```text
manifest 1
Chunk001..011.lua 11
```

* Seal physical/logical/PZ deployable referent equivalence:

```json
{
  "input_path_is_pz_deployable_target": true,
  "physical_path_to_logical_path_equivalence": "confirmed",
  "physical_path_prefix": "Iris/media/lua/client/Iris/Data",
  "logical_path_prefix": "Iris/Data",
  "pz_autoload_referent": "Iris/Data/IrisLayer3DataChunks.lua + Iris/Data/IrisLayer3DataChunks/Chunk001..011.lua"
}
```

If this equivalence cannot be confirmed before scanning, close as `blocked_runtime_identity_ambiguous`.

* Declare non-authority:

```text
IrisLayer3Data.lua monolith
```

* Declare mutable output surface:

```text
round-local staging reports and closeout markdown/json only
optional additive docs addendum after closeout
```

* Declare immutable surfaces:

```text
runtime chunks
manifest
source decisions
rendered artifacts
consumer code
sealed decision bodies
```

* Create a Phase 0 immutable hash snapshot for all immutable input/runtime/consumer targets and record round-start `git status --short`. Later `git diff` review must be interpreted relative to this Phase 0 snapshot; pre-existing dirty paths are not round mutations unless their Phase 0 hash changes during this round.

* Declare closeout ceiling:

```text
sealed_current_runtime_baseline_for_MIGV_QA_Phase_1
```

* Declare non-claims:

```text
manual QA pass 아님
deployed closeout 아님
runtime rollout 아님
release readiness 아님
Workshop readiness 아님
tooltip validation 아님
```

Validation:

```text
scope_lock_present = true
read_only_declared = true
runtime_mutation_forbidden = true
input_paths_exist = true
input_path_is_pz_deployable_target = true
physical_path_to_logical_path_equivalence = confirmed
phase0_immutable_hash_snapshot_present = true
prior_count_assumption_forbidden = true
```

---

### Change 2 - Phase 1 runtime file identity scan

Purpose:

Seal the identity of the current deployable runtime file set.

Files:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_hash_manifest.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_chunk_identity_report.json
```

Implementation Notes:

* Confirm manifest file existence and compute SHA-256.
* Confirm physical workspace paths map to the logical PZ deployable referent sealed in Phase 0.
* Parse manifest chunk references.
* Confirm `Chunk001..011.lua` existence and numbering with no gaps.
* Compute SHA-256 for each chunk.
* Compare manifest references with filesystem chunk list.
* Inventory missing and extra chunks.
* Check monolith status:

```text
absent
present_non_authority
present_auto_load_risk
```

* Check whether monolith and chunks can both be PZ auto-load targets.
* Record historical staged hash `0390272b...` as comparison-only, not pass/fail criteria.

Validation:

```json
{
  "manifest_present": true,
  "manifest_chunk_count": 11,
  "filesystem_chunk_count": 11,
  "missing_chunks": [],
  "extra_chunks": [],
  "input_path_is_pz_deployable_target": true,
  "physical_path_to_logical_path_equivalence": "confirmed",
  "monolith_status": "absent_or_non_authority",
  "historical_hash_is_comparison_only": true,
  "runtime_identity_status": "sealed"
}
```

Failure branches:

```text
blocked_runtime_identity_ambiguous
blocked_monolith_active_risk
blocked_chunk_count_mismatch
```

---

### Change 3 - Phase 2 runtime payload inventory scan

Purpose:

Seal current payload inventory from actual chunk content, not from historical readpoint counts.

Files:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_payload_inventory.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/missing_publish_state_inventory.jsonl
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/nil_text_ko_inventory.jsonl
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/legacy_enum_residue_inventory.jsonl
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/duplicate_runtime_key_inventory.jsonl
```

Implementation Notes:

* Parse chunk payload rows.
* Count rows per chunk and total rows.
* Extract row identity keys and detect duplicates.
* Detect malformed rows.
* Count current `source` or runtime-state values:

```text
adopted
unadopted
legacy_active
legacy_silent
missing
unknown
```

* Count `quality_state`.
* Count `publish_state`:

```text
exposed
internal_only
missing
null
unknown
```

* Inventory missing/null/unknown `publish_state`.
* Inventory `text_ko` states:

```text
present_non_empty
missing_key
nil
empty
whitespace_only
```

* Treat `internal_only` as runtime-retained and not as deletion target.
* Treat `unadopted` as runtime status only, not deletion or publish suppression.
* Record historical expected count as historical comparison, not parser input.
* Compare measured `total_rows`, `adopted`, and `unadopted` counts with current governance readpoint `2105 / 2084 / 21`.
* If measured counts differ from the current governance readpoint, set `current_readpoint_delta_requires_reconciliation = true` and close this round as `blocked_current_readpoint_reconciliation_required`.
* Same-round pass handoff is forbidden when current readpoint count/split deltas exist. Reconciliation must be handled by a separate reconciliation round before any later current-runtime baseline pass can be sealed.
* This reconciliation requirement is not frozen 2105 byte-level reconstruction and must not be used to reopen historical hash parity recovery.
* Perform no automatic correction for findings.

Validation:

```json
{
  "total_rows_measured": 0,
  "per_chunk_row_count": {},
  "runtime_state_or_source_split": {
    "adopted": 0,
    "unadopted": 0,
    "legacy_active": 0,
    "legacy_silent": 0,
    "missing": 0,
    "unknown": 0
  },
  "publish_state_split": {
    "exposed": 0,
    "internal_only": 0,
    "missing": 0,
    "null": 0,
    "unknown": 0
  },
  "text_ko_inventory": {
    "present_non_empty": 0,
    "missing_key": 0,
    "nil": 0,
    "empty": 0,
    "whitespace_only": 0
  },
  "duplicate_identity_key_count": 0,
  "row_identity_key_schema": "canonical row identity key schema used by the parser",
  "identity_key_source": "table_key | fullType_field | item_id_field | derived",
  "current_readpoint_comparison": {
    "expected_total_rows": 2105,
    "expected_adopted": 2084,
    "expected_unadopted": 21,
    "delta_requires_reconciliation": false
  }
}
```

Failure branches:

```text
blocked_runtime_identity_ambiguous
blocked_current_readpoint_reconciliation_required
sealed_with_inventory_findings
sealed_clean
```

---

### Change 4 - Phase 3 consumer filtering contract scan

Purpose:

Seal how current renderer, Browser, Wiki, and Tooltip-adjacent static contract consume the current runtime payload without creating new policy.

Files:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_consumer_filtering_contract_report.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_consumer_filtering_contract_summary.md
```

Implementation Notes:

* Confirm Layer 3 renderer chunk manifest load path.
* Confirm monolith fallback reachability.
* Confirm Browser default filtering behavior.
* Confirm Wiki default filtering behavior.
* Confirm `internal_only` runtime retention and default suppression.
* Confirm missing `publish_state` behavior:

```text
fail_loud
hard_error
crash
skip
default_exposed
default_internal_only
undefined
```

* Confirm nil/missing `text_ko` behavior:

```text
crash
hard_error
skip
placeholder
blank
undefined
```

* Confirm whether consumers depend on legacy `active / silent`.
* Confirm consumers do not recompute publish judgment and only read existing `publish_state`.
* Treat Tooltip as static contract only; do not perform tooltip validation.
* Cross-check that consumer scan does not contradict the sealed three-axis model.
* Apply the inventory count × consumer behavior matrix before classification:

```text
missing_publish_state_count > 0 + fail_loud/crash/hard_error
=> blocked_contract_runtime_breakage

nil_or_missing_text_ko_count > 0 + crash/hard_error
=> blocked_contract_runtime_breakage

missing_publish_state_count > 0 + skip/default_internal_only
=> sealed_with_inventory_findings, only with full inventory and MIGV-QA handoff note

nil_or_missing_text_ko_count > 0 + skip/blank/placeholder
=> sealed_with_inventory_findings, only with full inventory and MIGV-QA handoff note
```

Validation:

```json
{
  "manifest_loader_path_confirmed": true,
  "monolith_fallback_reachable": false,
  "browser_default_filter": "publish_state=exposed",
  "wiki_default_filter": "publish_state=exposed",
  "tooltip_filter": "not_validated_or_static_contract_only",
  "internal_only_runtime_retained": true,
  "internal_only_default_visible": false,
  "missing_publish_state_behavior": "fail_loud_or_skip_or_undefined",
  "nil_text_ko_behavior": "crash_or_skip_or_placeholder_or_undefined",
  "missing_publish_state_runtime_breakage_count": 0,
  "nil_or_missing_text_ko_runtime_breakage_count": 0,
  "legacy_enum_dependency_count": 0
}
```

Hard blocker:

```text
missing_publish_state_behavior = undefined -> blocked_contract_undefined
nil_text_ko_behavior = undefined -> blocked_contract_undefined
missing_publish_state_count > 0 and behavior in fail_loud/crash/hard_error -> blocked_contract_runtime_breakage
nil_or_missing_text_ko_count > 0 and behavior in crash/hard_error -> blocked_contract_runtime_breakage
```

---

### Change 5 - Phase 4 negative invariant and fail-loud verification

Purpose:

Prove that the seal round did not mutate runtime authority or sealed source surfaces, and classify every unexpected delta as a named finding.

Files:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/phase4_negative_invariant_report.json
```

Implementation Notes:

* Compare Phase 0 and post-scan hashes for all immutable target files.
* Verify no mutation to:

```text
row identity
rendered text
runtime Lua chunks
chunk topology
quality_state
publish_state
source decisions
consumer code
```

* Review `git diff --stat` and `git diff` for forbidden mutation using the Phase 0 immutable hash snapshot as the round-start baseline. Pre-existing dirty working tree changes are recorded but are not attributed to this round unless their Phase 0 hashes change after the round begins.
* Classify deltas against prior readpoints as:

```text
match
finding
not_applicable
```

* Required classified deltas:

```text
row_count vs historical 2105
source split vs historical 2084/21
row_count/source split vs current governance readpoint 2105/2084/21
missing publish_state > 0
nil text_ko > 0
legacy enum residue > 0
duplicate runtime key > 0
monolith status
current hash mismatch with historical 0390272b...
```

Validation:

```text
runtime_artifact_mutation_count = 0
source_decision_mutation_count = 0
consumer_code_mutation_count = 0
round_directory_only_output = true
classified_delta_count = total_delta_count
unclassified_delta_count = 0
current_readpoint_delta_reconciled_or_blocked = true
```

Failure branches:

```text
blocked_due_to_undeclared_mutation
blocked_unclassified_delta
blocked_current_readpoint_reconciliation_required
```

---

### Change 6 - Phase 5 hard gate

Purpose:

Evaluate the sealability gates before baseline classification.

Files:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/phase5_hard_gate_report.json
```

Implementation Notes:

Hard gate requires:

```text
Phase 1 file identity inventory complete
Phase 2 payload inventory complete
historical hash mismatch recorded as fact, not regression
Phase 3 consumer contract captured
three-axis contradiction count = 0
Phase 4 mutation count = 0
all deltas classified as match or finding
unclassified delta count = 0
current governance readpoint count/split delta reconciled, or blocked
inventory count x consumer behavior matrix has no runtime-breakage blocker
Python validation command exits 0
Lua syntax validation command exits 0
```

Required validation commands:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Validation:

```text
hard_gate = pass | blocked
python_unittest_exit_code = 0
lua_syntax_exit_code = 0
runtime_mutation_count = 0
contract_undefined_count = 0
contract_runtime_breakage_count = 0
runtime_identity_ambiguity_count = 0
current_readpoint_reconciliation_required = false
```

Failure branches:

```text
blocked_contract_undefined
blocked_contract_runtime_breakage
blocked_runtime_identity_ambiguous
blocked_current_readpoint_reconciliation_required
blocked_with_static_validation_failure
blocked_due_to_undeclared_mutation
```

---

### Change 7 - Phase 6 baseline classification and branch decision

Purpose:

Classify the current runtime baseline according to evidence, without turning findings into cleanup work.

Files:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/closeout/current_runtime_baseline_seal.json
```

Implementation Notes:

Allowed PASS branches:

```text
A. sealed_clean
B. sealed_with_inventory_findings
```

Blocked branches:

```text
C. blocked_contract_undefined
D. blocked_contract_runtime_breakage
E. blocked_runtime_identity_ambiguous
F. blocked_monolith_active_risk
G. blocked_chunk_count_mismatch
H. blocked_unclassified_delta
I. blocked_current_readpoint_reconciliation_required
J. blocked_with_static_validation_failure
K. blocked_due_to_undeclared_mutation
```

Unified blocked-state mapping:

```text
blocked_monolith_active_risk -> final blocked state and parent category blocked_runtime_identity_ambiguous
blocked_chunk_count_mismatch -> final blocked state and parent category blocked_runtime_identity_ambiguous
blocked_unclassified_delta -> final blocked state; no silent promotion to findings
blocked_contract_runtime_breakage -> final blocked state for inventory count x crash/fail_loud/hard_error behavior
blocked_current_readpoint_reconciliation_required -> final blocked state until a separate governance readpoint reconciliation round is sealed; not frozen 2105 byte-level reconstruction
```

Branch A requires:

```text
chunk identity clear
manifest/chunk topology normal
duplicate row identity = 0
missing publish_state = 0
null publish_state = 0
unknown publish_state = 0
nil/missing/empty/whitespace text_ko = 0
legacy active/silent payload residue = 0
consumer filtering contract clear
MIGV-QA Phase 1 can resume
```

Branch B permits findings only when:

```text
chunk topology normal
monolith absent or non-authority with no active risk
duplicate/missing row identity = 0
Lua syntax/static tests pass
consumer filtering contract has no undefined behavior
inventory count x consumer behavior matrix has no runtime-breakage blocker
current governance readpoint count/split deltas are reconciled or absent
missing publish_state / nil text_ko findings are inventoried
MIGV-QA receives finding-aware handoff
no deployed closeout or pass claim
```

Blocked transition conditions:

```text
chunk manifest/chunk file count broken
duplicate/missing canonical row identity key break
monolith deployable authority risk
Lua syntax/static tests fail
nil text_ko consumer crash risk undefined
missing publish_state default user-facing filtering behavior undefined
missing_publish_state_count > 0 with fail_loud/crash/hard_error behavior
nil_or_missing_text_ko_count > 0 with crash/hard_error behavior
measured total row/source split differs from current governance readpoint without sealed reconciliation
```

Validation:

```text
branch_decision_matches_evidence = true
pass_status = sealed_clean | sealed_with_inventory_findings
blocked_status = blocked_contract_undefined | blocked_contract_runtime_breakage | blocked_runtime_identity_ambiguous | blocked_monolith_active_risk | blocked_chunk_count_mismatch | blocked_unclassified_delta | blocked_current_readpoint_reconciliation_required | blocked_with_static_validation_failure | blocked_due_to_undeclared_mutation
release_overclaim_count = 0
```

---

### Change 8 - Phase 7 adversarial review

Purpose:

Perform hostile review of the seal evidence, claim ceiling, and read-only boundary before closeout.

Files:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/phase7_adversarial_review.md
```

Implementation Notes:

* Use `REVIEW_TEMPLATE.md` structure.
* Review focus:

```text
read-only boundary violation
validation ceiling overclaim
MIGV-QA pass implication
deployed/release implication
single-writer violation
fail-loud bypass
sealed body mutation
historical hash reconciliation attempt
consumer contract undefined leakage
finding inventory completeness
```

Validation:

```text
adversarial_review_verdict = PASS
critical_issue_count = 0
blocker_count = 0
major_issue_count = 0
unsupported_claim_count = 0
```

If critical/blocker/major issues remain, closeout must be blocked or corrected before sealing.

---

### Change 9 - Phase 8 closeout and MIGV-QA handoff

Purpose:

Write the single sealed evidence path/hash for MIGV-QA Phase 1 and close the round within the allowed claim ceiling.

Files:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/closeout/current_runtime_baseline_seal_closeout.md
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/closeout/current_runtime_baseline_seal.json
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/closeout/migv_qa_phase1_handoff.md
```

Optional docs after closeout:

```text
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

Implementation Notes:

* Closeout must include:

```text
branch classification
single sealed evidence path/hash
manifest sha256
chunk sha256 list
payload inventory summary
consumer filtering contract summary
finding inventories
negative invariant result
validation command results
adversarial review verdict
historical hash comparison-only note
current governance readpoint count/split reconciliation status
non-claim list
```

* Handoff must replace MIGV-QA Phase 1 identity pre-gate reference with:

```text
current_runtime_hash_manifest.json
current_runtime_chunk_identity_report.json
current_runtime_payload_inventory.json
current_runtime_baseline_seal.json
```

* Handoff must state MIGV-QA should validate:

```text
all runtime rows
default visible exposed rows
internal_only suppressed rows
unadopted rows
finding rows
```

* Handoff must state MIGV-QA must not claim:

```text
release readiness
Workshop readiness
tooltip validation
deployed closeout
```

* Handoff must also state:

```text
Tooltip-related observations are static contract notes only
and must not be read as tooltip validation.
```

* Required sentence must appear verbatim:

```text
MIGV-QA Phase 1 identity pre-gate must use the sealed current runtime baseline
from DVF 3-3 Current Runtime Baseline Seal Round, not the historical staged hash.
```

Validation:

```text
closeout_present = true
single_evidence_path_hash_present = true
migv_handoff_present = true
historical_hash_not_used_as_current_gate = true
current_readpoint_delta_reconciled_or_blocked = true
tooltip_static_note_not_validation = true
non_claims_present = true
DECISIONS_entry_draft_present_or_not_applicable = true
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

Required automated/static checks:

* Input path existence check.
* Physical path to logical `Iris/Data/...` deployable referent equivalence check.
* Phase 0 immutable hash snapshot check.
* Manifest parser check.
* Filesystem chunk list check.
* SHA-256 determinism check.
* Manifest vs filesystem chunk reference comparison.
* Monolith deployable path risk check.
* Runtime payload parser check.
* Row count and per-chunk count scan.
* Duplicate runtime identity key scan.
* `adopted / unadopted` split scan.
* Legacy `active / silent` residue scan.
* `quality_state` and `publish_state` split scan.
* Missing/null/unknown `publish_state` inventory.
* `text_ko` missing/nil/empty/whitespace-only inventory.
* Consumer filtering contract static scan.
* Inventory count x consumer behavior matrix check.
* Current governance readpoint count/split reconciliation check.
* Negative invariant hash comparison.
* `git diff --stat` and `git diff` review for forbidden mutation relative to the Phase 0 immutable hash snapshot.
* Hard gate report.
* Adversarial review.

Validation claim rule:

* Do not claim Python tests passed unless the exact command exits `0`.
* Do not claim Lua syntax passed unless the exact command exits `0`.
* If a required tool is missing, report validation as blocked.
* Static validation pass is not manual in-game validation pass.

### Manual Validation

Manual validation is limited to inspection/review of generated evidence reports and adversarial review.

No manual in-game QA is part of this plan.

### Validation Limits

This execution does not perform:

* Manual in-game validation.
* Multiplayer validation.
* Deployment validation.
* Runtime rollout validation.
* Long-session runtime validation.
* External mod compatibility sweep.
* Workshop validation.
* Tooltip validation.
* B42 validation.
* Frozen 2105 byte-level reconstruction.
* Full runtime equivalence proof.

---

## 8. Risk Surface Touch

### Authority Surface

Touched only as additive evidence seal. The round creates a new sealed current-runtime baseline evidence path/hash. It must not rewrite existing sealed decision bodies or change source/publish/quality authority.

### Runtime Behavior Surface

None planned. Runtime chunks and consumer behavior are read-only scan targets.

### Compatibility Surface

None planned. External mod contracts and SPI are unchanged.

### Sealed Artifact Surface

Additive. New JSON/MD evidence is written under the round-local staging directory. Existing sealed artifacts are read-only.

### Public-Facing Output Surface

None planned. Browser, Wiki, Tooltip, and runtime display output are not changed.

---

## 9. Risk Analysis

### Architecture Risk

* Consumer filtering contract may remain undefined even if file hashes and row counts are sealed.
* Current physical input paths could fail to match the logical PZ deployable referent unless Phase 0 equivalence is sealed.
* Treating historical `0390272b...` as current authority would invalidate the new baseline.
* Measured count/split deltas could contradict current governance readpoints unless reconciled or blocked.
* Treating Phase 3 consumer scan as policy creation would exceed scope.
* Top-doc addenda could overstate the result as deployed closeout.

### Runtime Risk

* Monolith active-path risk could be hidden if monolith presence is treated as harmless without load-path analysis.
* Payload parser errors could silently undercount malformed rows.
* Missing `publish_state` or nil `text_ko` could be recorded without understanding consumer crash/filter behavior.
* Known crash/fail-loud behavior with non-zero inventory is runtime breakage, not a mere inventory finding.
* Legacy enum residue could be missed if only one field name is scanned.

### Compatibility Risk

* `internal_only` could be misread as runtime deletion target.
* `unadopted` could be misread as publish suppression or removal.
* Browser/Wiki filtering could be mistaken for publish writer authority.

### Regression Risk

* A read-only seal round could drift into cleanup if findings are auto-fixed.
* Helper tooling could mutate runtime or generated artifacts if not scoped carefully.
* Prior readpoint counts could be hardcoded and mask current checkout reality.
* Validation pass could be overclaimed as manual QA or release readiness.

---

## 10. Rollback Plan

Normal read-only case:

* No source/runtime/code rollback is needed.
* Delete or supersede:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/
```

* If optional docs addenda were written, add a correction/supersession entry or revert only the additive addendum.

Blocked closeout case:

* Preserve evidence reports as blocked evidence.
* Do not update MIGV-QA Phase 1 to resume.
* Do not declare sealed baseline pass.

Accidental mutation case:

* Record mutated paths.
* Stop the seal round.
* Revert only the accidental runtime/source/consumer mutation, preserving unrelated user changes.
* Re-run negative invariant validation.
* Close the attempted round as invalid or blocked due to undeclared mutation.
* Reopen a fresh seal round only after the workspace is restored.

Wrong claim case:

* Do not silently rewrite historical sealed text.
* Add a correction addendum.
* Reset claim ceiling to at most `sealed_current_runtime_baseline_for_MIGV_QA_Phase_1`.

---

## 11. Governance Constraints

Required constraints:

* `Philosophy.md` compliance.
* Iris remains render-only at runtime.
* No interpretation, recommendation, or comparison generation.
* Read-only runtime artifact scan.
* No chunk regeneration.
* No Lua bridge regeneration.
* No source decision mutation.
* No rendered text mutation.
* No `publish_state`, `quality_state`, `source`, or `text_ko` mutation.
* No monolith restoration or authority promotion.
* No historical staged hash parity recovery.
* Additive seal only.
* Existing sealed decisions remain intact.
* Runtime/build-time separation preserved.
* Single-writer principle preserved.
* Browser/Wiki consumers remain readers of already-computed `publish_state`.
* Missing/null/legacy/nil findings are inventory outputs, not mutation triggers.
* Undefined consumer contract blocks seal.
* Known crash/fail-loud consumer behavior with non-zero affected inventory blocks seal.
* Current governance readpoint count/split deltas require `blocked_current_readpoint_reconciliation_required`; reconciliation is a separate round, not a same-round pass addendum.
* No new helper script or code file may be added in this round.
* `round_directory_only_output = true` remains strict for planned outputs.
* Dirty working tree handling must preserve unrelated user changes.
* Validation pass must not be reported without exact command exit code `0`.
* Manual in-game QA, deployed closeout, release readiness, Workshop readiness, and tooltip validation remain out of scope.

---

## 12. Expected Closeout State

Expected successful closeout:

```text
sealed_clean
```

or:

```text
sealed_with_inventory_findings
```

Successful closeout requires:

```text
manifest file present
physical path to logical PZ deployable referent equivalence confirmed
Phase 0 immutable hash snapshot present
manifest sha256 sealed
Chunk001..011 present
chunk sha256 sealed
manifest chunk count sealed
filesystem chunk count sealed
missing/extra chunk inventory sealed
monolith absent or non-authority status sealed
current measured total row count sealed
current measured per-chunk row count sealed
current governance readpoint count/split delta absent or sealed as reconciled
duplicate runtime identity key inventory sealed
adopted/unadopted split sealed
legacy active/silent payload residue inventory sealed
publish_state split sealed
missing/null/unknown publish_state inventory sealed
text_ko missing/nil/empty/whitespace-only inventory sealed
Browser/Wiki/renderer consumer filtering contract sealed
missing publish_state behavior classified
nil text_ko behavior classified
inventory count x consumer behavior matrix has no runtime-breakage blocker
single sealed evidence path/hash created for MIGV-QA Phase 1
historical staged hash is not used as current identity gate
runtime artifact mutation count = 0
Python unittest validation exits 0
Lua syntax validation exits 0
adversarial review Verdict = PASS
adversarial review major issue count = 0
manual in-game validation pass claim count = 0
deployed closeout claim count = 0
release readiness claim count = 0
Workshop readiness claim count = 0
tooltip validation claim count = 0
```

Blocked closeout states:

```text
blocked_contract_undefined
blocked_contract_runtime_breakage
blocked_runtime_identity_ambiguous
blocked_monolith_active_risk
blocked_chunk_count_mismatch
blocked_unclassified_delta
blocked_current_readpoint_reconciliation_required
blocked_with_static_validation_failure
blocked_due_to_undeclared_mutation
```

If the round is not sealed successfully and closes as a blocked closeout, the reason must be explicit:

* consumer filtering behavior undefined,
* consumer behavior is known crash/fail-loud/hard_error for non-zero affected inventory,
* missing or extra chunk ambiguity,
* monolith active deployable risk,
* duplicate/missing row identity,
* current governance readpoint count/split reconciliation required,
* Python validation failure,
* Lua syntax validation failure,
* mutation detected,
* unclassified delta,
* adversarial review blocker,
* or missing sealed evidence path/hash.

Non-claims at any closeout:

* No manual in-game validation pass.
* No deployed closeout.
* No runtime rollout.
* No release readiness.
* No Workshop readiness.
* No tooltip validation.
* No B42 readiness.
* No frozen 2105 byte-level reconstruction.
* No historical hash parity recovery.
* No full runtime equivalence claim.
