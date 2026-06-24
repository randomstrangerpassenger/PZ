# DVF 3-3 Current-Route Baseline / Source-Overlay Repair Authorization

Status: granted_for_authorized_repair_round
Date: 2026-06-23
Authority: explicit user authorization in this Codex session

This document records bounded authorization for the next DVF 3-3
Current-Route Baseline / Source-Overlay repair implementation round. It
does not claim that the full current-route repair has already passed.

## Authorized Scope

The authorized repair round may reconnect the live current-route source
baseline by materializing the selected corrected vNext 2105-row source
snapshot into the live facts and decisions inputs only.

Authorized source artifacts:

- `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_input_snapshot/dvf_3_3_facts.corrected.jsonl`
- `Iris/build/description/v2/staging/dvf_3_3_vnext_rejected_delta_correction_reparity/phase5/corrected_input_snapshot/dvf_3_3_decisions.corrected.normalized.jsonl`

Authorized live write targets:

- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`

## Forbidden Scope

This authorization does not permit writes to:

- `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
- rendered current-route outputs
- runtime Lua bridge files or runtime chunk directories
- package-route artifacts
- required-validation manifests
- roadmap, architecture, decision, or release-readiness authority documents

The current 2105 overlay support artifact is already classified as matching
the manifest and must remain excluded from the reconnect write set unless a
separate authorization supersedes this document.

## Required Runner Boundary

The implementation round must use a bounded writer that:

- accepts only the exact authorized source artifacts and live write targets
- captures pre-write hashes and row counts for both targets
- writes no live path outside the exact target allowlist
- emits post-write hashes and row counts
- preserves enough pre-write evidence under the repair staging evidence root
  to support rollback or audit

No validator may mutate live `data/` material. The no-write diagnostic
validator and the live writer must remain separate execution paths.

## Required Post-Write Validation

After materialization, the repair round must run a no-write validator that
confirms:

- live facts and decisions each contain 2105 rows
- live facts and decisions hashes match
  `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
- source, overlay, rendered, and runtime deployable universes remain
  row-identity cross-attested
- the 6-row `CURRENT_FACTS=6` surface is no longer consumed as full current
  authority
- staging body overlay consumption is either contractually included in the
  full current route or fail-closed outside diagnostic/staging paths

## Remaining Non-Claims

This authorization clears the write-authorization blocker for the bounded
facts/decisions reconnect only. It does not by itself satisfy the independent
adversarial review requirement, seal a final contract packet, or authorize a
full runtime/rendered/package regeneration.
