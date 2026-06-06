# Iris DVF 3-3 Current Runtime Baseline Seal Round Walkthrough

> 상태: closed walkthrough  
> 기준일: 2026-05-23  
> round: DVF 3-3 Current Runtime Baseline Seal Round  
> plan: `docs/Iris/iris-dvf-3-3-current-runtime-baseline-seal-round-plan.md`  
> artifact root: `Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/`

This walkthrough is not a new authority or gate source. It records how the read-only current-runtime baseline seal round moved from scope lock to closeout, and how MIGV-QA Phase 1 must consume the result.

## 1. Why This Round Existed

MIGV-QA Phase 1 had an identity pre-gate blocker: it needed a current checkout runtime identity referent, not the historical staged hash.

The round therefore measured the deployable runtime authority directly:

```text
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk001..011.lua
```

The round did not attempt historical byte parity recovery. The historical staged hash beginning with `0390272b...` was recorded as comparison-only.

## 2. Scope Boundary

This was a read-only authority/evidence seal.

Allowed output:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/
```

Not changed:

- runtime Lua chunks
- chunk manifest
- rendered text
- source decisions
- publish decisions
- quality decisions
- consumer code
- top-level sealed decision bodies

No helper script was added to the repository. The evidence was generated through one-off local commands and written only as round-local artifacts.

## 3. Phase 0 - Scope Lock

Phase 0 wrote the read-only boundary and immutable hash snapshot.

Artifacts:

- `phase0_scope_lock.json`
- `phase0_immutable_hash_snapshot.json`

Important sealed facts:

- `runtime_artifact_mutation = forbidden`
- authoritative input is one manifest plus 11 chunk files
- physical path `Iris/media/lua/client/Iris/Data/...` maps to logical PZ deployable path `Iris/Data/...`
- `IrisLayer3Data.lua` monolith is non-authority
- pre-existing dirty worktree paths are not attributed to this round unless Phase 0 hashes change

## 4. Phase 1 - Runtime File Identity

Phase 1 measured the current deployable file set.

Artifacts:

- `reports/current_runtime_hash_manifest.json`
- `reports/current_runtime_chunk_identity_report.json`

Measured identity:

```text
manifest present: true
manifest chunk references: 11
filesystem chunk files: 11
missing chunks: 0
extra chunks: 0
monolith status: absent
runtime identity status: sealed
```

The single sealed evidence path for MIGV-QA Phase 1 is:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/reports/current_runtime_hash_manifest.json
sha256 790b5689097a8856e6213074fda25b723060073206a7ca44bd26d9f6f08c9171
```

The manifest file hash was:

```text
fa9f74938023cc81a08e12bc271a22f65befb5df36c0a18e85550882c82f6e2c
```

The aggregate runtime file-set hash was:

```text
16dc62ddc90e8bf8726c609b8635015d2e4d21ffde20d585b1f116e955f1f562
```

This aggregate does not match the historical `0390272b...` prefix, and that mismatch is a recorded fact, not a regression gate.

## 5. Phase 2 - Runtime Payload Inventory

Phase 2 parsed actual chunk payload rows rather than trusting historical counts as parser input.

Artifact:

- `reports/current_runtime_payload_inventory.json`

Measured inventory:

```text
total rows: 2105
Chunk001..010: 200 rows each
Chunk011: 105 rows
adopted: 2084
unadopted: 21
legacy active: 0
legacy silent: 0
duplicate runtime identity keys: 0
malformed rows: 0
```

The current governance readpoint `2105 / 2084 / 21` matched the measured runtime payload, so no current-readpoint reconciliation round was required.

Finding inventories:

```text
publish_state exposed: 1486
publish_state internal_only: 600
publish_state missing: 19
text_ko present_non_empty: 2086
text_ko nil: 19
legacy active/silent payload residue: 0
duplicate runtime keys: 0
```

Related inventory artifacts:

- `reports/missing_publish_state_inventory.jsonl`
- `reports/nil_text_ko_inventory.jsonl`
- `reports/legacy_enum_residue_inventory.jsonl`
- `reports/duplicate_runtime_key_inventory.jsonl`

The 19 missing `publish_state` rows and 19 nil `text_ko` rows were not repaired in this round. They are finding rows for MIGV-QA handoff.

## 6. Phase 3 - Consumer Filtering Contract

Phase 3 statically inspected the Layer 3 runtime consumer path.

Artifacts:

- `reports/current_runtime_consumer_filtering_contract_report.json`
- `reports/current_runtime_consumer_filtering_contract_summary.md`

Confirmed consumer contract:

```text
layer3_renderer load path: safeRequire("Iris/Data/IrisLayer3DataChunks")
monolith require fallback reachable: false
global IrisLayer3Data fallback reachable: true
Browser default filter: publish_state != internal_only
Wiki default filter: publish_state != internal_only
Tooltip: static contract note only, not validated
internal_only runtime retained: true
internal_only default visible: false
missing publish_state behavior: default_exposed if text_ko exists
nil text_ko behavior: skip
legacy active/silent dependency count: 0
```

The inventory count x consumer behavior matrix produced no runtime breakage blocker:

```text
contract undefined count: 0
missing publish_state runtime breakage count: 0
nil/missing text_ko runtime breakage count: 0
```

Tooltip observations in this round are static notes only and must not be read as tooltip validation.

## 7. Phase 4 - Negative Invariant

Phase 4 compared Phase 0 immutable hashes against post-scan hashes.

Artifact:

- `phase4_negative_invariant_report.json`

Result:

```text
immutable hash delta count: 0
runtime artifact mutation count: 0
source decision mutation count: 0
consumer code mutation count: 0
round directory only output: true
classified delta count: 9
unclassified delta count: 0
```

The worktree already contained unrelated dirty and untracked paths. They remained visible in `git diff`, but the Phase 0 immutable hash comparison showed this round did not mutate the runtime/source/consumer targets.

Classified findings:

- missing `publish_state > 0`: `19`
- nil `text_ko > 0`: `19`
- current aggregate hash mismatch with historical `0390272b...`

Classified matches:

- row count vs `2105`
- source split vs `2084 / 21`
- current governance readpoint split
- legacy enum residue `0`
- duplicate runtime key `0`
- monolith status `absent`

## 8. Phase 5 - Hard Gate

Phase 5 evaluated sealability.

Artifact:

- `phase5_hard_gate_report.json`

Gate result:

```text
hard_gate: pass
contract_undefined_count: 0
contract_runtime_breakage_count: 0
runtime_identity_ambiguity_count: 0
current_readpoint_reconciliation_required: false
```

Required validation commands both exited `0`:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Observed:

```text
Ran 394 tests in 9.508s
OK
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Observed:

```text
Lua syntax validation OK: 183 files
```

## 9. Phase 6 - Branch Classification

The branch closed as:

```text
sealed_with_inventory_findings
```

It was not `sealed_clean` because:

```text
missing_publish_state_count = 19
nil_or_missing_text_ko_count = 19
```

It was not blocked because:

```text
chunk topology normal
monolith absent
duplicate runtime identity key count = 0
legacy active/silent residue count = 0
consumer contract undefined count = 0
runtime breakage blocker count = 0
current governance readpoint delta = false
required validation commands exit 0
runtime/source/consumer mutation count = 0
```

## 10. Phase 7 - Adversarial Review

Artifact:

- `phase7_adversarial_review.md`

Review result:

```text
verdict: PASS
critical_issue_count: 0
blocker_count: 0
major_issue_count: 0
unsupported_claim_count: 0
```

The review specifically checked for read-only boundary violation, validation ceiling overclaim, MIGV-QA pass implication, deployed/release implication, single-writer violation, fail-loud bypass, sealed body mutation, historical hash reconciliation attempt, consumer contract undefined leakage, and finding inventory completeness.

## 11. Phase 8 - Closeout and MIGV-QA Handoff

Closeout artifacts:

- `closeout/current_runtime_baseline_seal.json`
- `closeout/current_runtime_baseline_seal_closeout.md`
- `closeout/migv_qa_phase1_handoff.md`

Closeout JSON hash:

```text
539b338bab5c4bc185d126c670b75d74eb38970690f717e1c3e4caee222621e3
```

Handoff hash:

```text
486cfbd1f35da0a98d3ff8d07b8c4be0a56c7ad30d60fe87c70712aabc7f33f3
```

Required handoff sentence:

```text
MIGV-QA Phase 1 identity pre-gate must use the sealed current runtime baseline from DVF 3-3 Current Runtime Baseline Seal Round, not the historical staged hash.
```

MIGV-QA Phase 1 must validate:

- all runtime rows
- default visible exposed rows
- internal_only suppressed rows
- unadopted rows
- finding rows

MIGV-QA must not claim:

- release readiness
- Workshop readiness
- tooltip validation
- deployed closeout

## 12. Artifact Map

All round artifacts are under:

```text
Iris/build/description/v2/staging/dvf_3_3_current_runtime_baseline_seal_round/
```

Files:

- `phase0_scope_lock.json`
- `phase0_immutable_hash_snapshot.json`
- `phase4_negative_invariant_report.json`
- `phase5_hard_gate_report.json`
- `phase7_adversarial_review.md`
- `reports/current_runtime_hash_manifest.json`
- `reports/current_runtime_chunk_identity_report.json`
- `reports/current_runtime_payload_inventory.json`
- `reports/current_runtime_consumer_filtering_contract_report.json`
- `reports/current_runtime_consumer_filtering_contract_summary.md`
- `reports/missing_publish_state_inventory.jsonl`
- `reports/nil_text_ko_inventory.jsonl`
- `reports/legacy_enum_residue_inventory.jsonl`
- `reports/duplicate_runtime_key_inventory.jsonl`
- `closeout/current_runtime_baseline_seal.json`
- `closeout/current_runtime_baseline_seal_closeout.md`
- `closeout/migv_qa_phase1_handoff.md`

## 13. What Changed

Only round-local evidence artifacts were added.

The round established a current-runtime baseline evidence path/hash for MIGV-QA Phase 1 and recorded the current deployable runtime inventory.

## 14. What Did Not Change

- runtime Lua chunks
- chunk manifest
- rendered Korean text
- source decisions
- publish decisions
- quality decisions
- Browser behavior
- Wiki behavior
- Tooltip behavior
- top-level sealed decision bodies
- deployed state
- release state

## 15. Non-Claims

This walkthrough and the closeout do not declare:

- manual in-game validation pass
- deployed closeout
- runtime rollout
- release readiness
- Workshop readiness
- tooltip validation
- B42 readiness
- frozen 2105 byte-level reconstruction
- historical hash parity recovery
- full runtime equivalence

## 16. How To Read This Next

For the next MIGV-QA session, read this walkthrough as traceability and then use the closeout/handoff artifacts as the identity pre-gate input.

The identity pre-gate must cite the current runtime baseline seal artifacts from this round. It must not cite the historical staged hash as the current runtime identity authority.

The 19 missing `publish_state` rows and 19 nil `text_ko` rows are finding-aware validation targets, not cleanup instructions.
