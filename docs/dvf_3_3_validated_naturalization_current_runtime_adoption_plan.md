# DVF 3.3 Validated Naturalization Current Runtime Adoption Plan

> Status: direct runtime adoption authorized / implementation pending / live mutation gated by off-live parity and rollback proof
>
> Supersedes historical plan SHA-256 `7294fc8cc8b825a159c844fca66fc5438effe0ac1821ad78fdc50af84d16ce13`.
> The superseded plan and attempts `attempt-0005` and `attempt-0006`, including every correction and failure artifact, remain immutable historical evidence. Their failures are neither RTC defects nor payload defects.

## 1. Objective and claim boundary

Adopt the already validated G5 naturalization candidate into current rendered data and Iris Lua data, then prove that Iris's existing consumer path loads and displays the improved text.

The only allowed terminal claim is:

`validated_naturalization_current_runtime_adoption_complete`

This plan does not execute or claim package, release, RTC, G6, owner seal, handoff, bundle/lifecycle resealing, or terminal closure. It does not create or consume RTC authority artifacts and does not change `current_route_required_validations.json`.

## 2. Immutable inputs and protected history

- Execution base: commit `c867a8d48fcf89c0e1f710acd5b100f261869af9`, tree `cd724ad09513e47b88046fabb2612f893a8b9bc5`.
- Validated candidate: the existing G5 candidate at the exact path and SHA declared by the adoption implementation.
- Source authority pair: the exact current facts and input-manifest paths and SHA-256 values declared by the adoption implementation.
- `attempt-0005`, `attempt-0006`, and all correction/failure evidence are read-only.
- `Iris/tools/package_iris.ps1` must equal its commit `d901881cfd8c9676559685eb8d2915181a7b754b` bytes. Package commands and package outputs are prohibited.
- RTC validators, policies, dispositions, bindings, authority artifacts, bundles, lifecycle records, and required-validation manifests are outside scope.

## 3. Change 1 — Direct adoption-generation exporter contract

Add a mutually exclusive `adoption-generation` mode to the existing DVF Lua exporter. Existing callers and default behavior remain unchanged.

The mode accepts only a hash-bound contract containing:

- exact candidate SHA-256;
- exact facts SHA-256;
- exact input-manifest SHA-256;
- an absolute, adoption-owned, off-live output root;
- `bridge_context=staging`;
- `authority_effect=none`;
- expected total/adopted/unadopted/text shape.

The adoption validator materializes and validates the contract before invoking the exporter. The exporter must validate it before any output write. Missing contract, hash drift, output-root escape or reparse traversal, context mismatch, shape mismatch, or coexistence with another exporter mode fails without fallback. It must not read or create policy, disposition, binding, lifecycle, bundle, package, or RTC authority artifacts.

Required regression coverage:

- missing adoption contract fails before write;
- candidate/facts/input-manifest hash mismatch fails;
- unauthorized output root fails;
- bridge-context mismatch fails;
- mixed adoption/legacy mode arguments fail;
- valid off-live export succeeds;
- default/fallback route is not invoked by adoption mode;
- existing exporter callers retain their prior behavior;
- every failure leaves live rendered, Lua, and package paths unchanged.

## 4. Change 2 — Single successor off-live generation

After Change 1 implementation and its regression suite pass, create exactly one new successor attempt. Never resume or modify attempts 0005 or 0006.

Generate off-live:

- `dvf_3_3_rendered.json`;
- `IrisLayer3DataChunks.lua`;
- every referenced `IrisLayer3DataChunks/Chunk*.lua`;
- a materialized generation descriptor and exhaustive parity receipts.

Validate across the full denominator:

- candidate/source and candidate/rendered bidirectional key-set equality;
- candidate facts and input-manifest binding;
- Git blob versus working-copy decoded EOL identity;
- candidate/rendered/Lua exact key, state, and public-text equality;
- all 2,084 adopted public texts match the candidate;
- all 21 unadopted rows gain no text;
- forbidden metadata count is zero;
- duplicate, overwrite, orphan, stale-chunk, and missing-chunk counts are zero;
- A/B regeneration has byte-identical output or an explicitly sealed canonical-payload identity.

Any failure is classified `blocked_adoption_generation` and stops without live mutation.

## 5. Change 3 — Atomic transaction and rollback proof

Treat the following as one transaction:

- current rendered JSON;
- Lua chunk manifest;
- the complete Lua chunk set;
- current generation descriptor.

The writer is allowlisted to those paths only. Write content files first and publish the manifest last. Before live cutover, execute the transaction in an isolated mirror and inject a failure between content installation and manifest publication.

Rollback validation requires:

- no partially applied generation remains current;
- exact preimage bytes are restored;
- temporary files count is zero;
- orphan/stale chunks count is zero;
- unrelated mutation count is zero.

Any failure is classified `blocked_adoption_transaction` and stops without live cutover.

## 6. Change 4 — Live cutover

Only after Changes 2 and 3 pass, acquire the adoption lock, revalidate all input hashes and the live preimage, install rendered/chunks/descriptor, and publish the Lua manifest last. On any write or post-write verification failure, automatically restore the exact preimage and remove transaction temporaries.

No package or RTC path may be written. The current required-validation manifest remains byte-identical.

## 7. Change 5 — Existing consumer and display validation

After cutover:

1. Run `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`.
2. Load the current chunk manifest and every referenced Lua chunk through the existing Iris loading path.
3. Compare current rendered and reconstructed current Lua across the full key/state/text denominator.
4. Exercise the existing Iris Browser consumer path.
5. Smoke-test sealed representative adopted, unchanged, unadopted, and case-variant items.
6. Verify improved text is displayed and predecessor text or stale chunks are not consumed.

An environment that cannot execute the real consumer/display smoke is classified `blocked_adoption_consumer_environment`; a load/parity failure is `blocked_adoption_consumer_connection`. Neither classification opens RTC or a separate technical-debt plan.

## 8. Completion gates

Completion requires all of the following:

- current rendered bytes/payload equal the validated candidate;
- current Lua equals current rendered over the full denominator;
- the existing Iris consumer loads the new Lua generation;
- representative in-game display smoke observes the improved text;
- rollback proof passes;
- unrelated runtime/Lua mutation count is zero;
- attempts 0005/0006 and required-validation/RTC/package surfaces remain unchanged.

Only then record `validated_naturalization_current_runtime_adoption_complete`. Do not claim package, release, RTC, G6, owner seal, handoff, bundle/lifecycle, or terminal closure completion.
