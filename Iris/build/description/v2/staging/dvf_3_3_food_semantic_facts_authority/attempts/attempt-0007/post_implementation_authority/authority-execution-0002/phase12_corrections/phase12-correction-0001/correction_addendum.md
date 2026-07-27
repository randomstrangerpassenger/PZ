# Phase 12 Correction Addendum — `phase12-correction-0001`

## Status and authority

This is a bounded correction cycle under the existing food-semantic authority reconstruction plan. It does not replace the roadmap, plan, attempt, approved D1/D5–D16 decisions, sealed Phase 11 successor, or the Phase 12 BLOCKED record.

The correction exists only to dispose `P12-D16-I1` and `P12-D16-I2`. Its implementation base is commit `32a2323afdb1e226470aec930574020f1dd7922d`.

## Lifecycle

```text
existing plan and sealed successor
-> preserved Phase 12 BLOCKED review
-> preimage-bound correction scope
-> focused scope review
-> owner scope approval
-> bounded implementation
-> replacement-bound correction bundle
-> external implementation review
-> owner result approval
-> Phase 12 resume
```

Scope approval authorizes only the reviewed files and symbols at their exact preimage SHA-256 values. It does not approve implementation results and does not bind replacement SHA-256 values. Replacement identities are created by implementation and may be approved only after external implementation review.

## Minimal dependency closure

The actual Naturalization module imports a candidate-only composition route that is absent from the reviewed base. Restoring only the first two names reported by Python would leave later imports unresolved. The bounded closure therefore contains five composition modules:

- body-plan candidate requirements and equivalence proof;
- candidate lead realization;
- candidate item composition;
- candidate corpus composition;
- the attempt-local candidate writer.

Every code change is additive. Existing default, legacy, and v2 function bodies are immutable. The candidate route remains attempt-local and cannot write current or protected paths.

The sixth writable file is the food-semantic handoff test. Its two affected methods may only distinguish:

- pending candidate state: live target equals manifest preimage; or
- owner-authorized adopted state: live target equals manifest replacement.

It may not weaken the four exact identities, append-only relation, D16 owner binding, or out-of-scope rejection.

## Boundaries

This correction cannot change food facts, schema, mappings, curation, approved assertions, detector policy, thresholds, waivers, Naturalization Phase 4–8 meaning, Registry ownership, Publish Boundary ownership, runtime, Lua, packaging, or release state.

The four already adopted D16 files are read-only. Their exact SHA-256 values remain inputs to the regenerated D16 correction manifest.

The original attempt and `phase12_external_implementation_review.blocked.json` are immutable evidence. New evidence is append-only under `phase12_corrections/phase12-correction-0001/`.

## Review and exit

Implementation may begin only when the focused scope review reports:

```text
Critical = 0
Important = 0
out_of_scope_change_count = 0
```

and the repository owner explicitly approves the reviewed preimage-bound scope.

After implementation, all focused Naturalization, food-semantic, compose-regression, and full repository commands in `correction_scope_manifest.json` must exit `0`. A fresh Codex Reviewer review must bind the actual replacement SHA-256 set with no open Critical or Important findings before owner result approval and Phase 12 resumption.
