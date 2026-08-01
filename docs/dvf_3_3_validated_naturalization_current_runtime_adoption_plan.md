# DVF 3.3 Validated Naturalization Runtime and Package Adoption Plan

> Status: runtime adoption complete at attempt-0008 / canonical package and current-route alignment authorized
>
> Supersedes the runtime-only scope whose plan SHA-256 was `f5adde504bafaa6e5134f2c921f07755adf5d3242861be8bb86ae0ade88ff39f`.
> Attempts `attempt-0005` through `attempt-0008` and their correction/failure evidence remain immutable.

## 1. Objective and claim boundary

Complete the original adoption chain:

```text
validated candidate
→ current rendered
→ current Lua manifest and chunks
→ existing Iris consumer/display smoke
→ canonical package projection
→ full current-route validation
```

Completion requires all three:

- validated naturalization is connected to the in-game runtime;
- the canonical package contains that exact runtime payload;
- the full current route passes twice from clean checkouts with the same denominator.

This work does not claim Workshop publication, release readiness, B42 readiness, owner seal, terminal closure, or a new RTC/G6 product defect.

## 2. Preserved runtime adoption

Attempt-0008 already proves:

- short external mirror rollback and exact cleanup;
- manifest-last atomic rendered/Lua cutover under an exclusive lock;
- 2,084 public texts match and 21 unadopted rows gain no text;
- rendered/Lua full parity and Lua syntax PASS;
- the existing Iris consumer loads adopted, unchanged, unadopted, and case-variant samples.

Revalidate these results on the final tree. Do not rewrite attempt-0008.

## 3. Canonical package applicability

`Iris/tools/package_iris.ps1` remains the canonical package writer. It must derive exactly one applicability class before writing:

- `current_runtime_payload`: no RTC certification inputs are present. Validate current rendered, generation descriptor, Lua manifest, and all descriptor-bound chunks before copy; validate package/live exact identity after copy.
- `rtc_certified_payload`: a complete explicit RTC input set is present. Preserve the existing RTC required-gate, contract, and surface validators.

Partial RTC arguments, an explicit applicability value inconsistent with supplied inputs, or mixed runtime/RTC authority claims fail before artifact write. There is no global RTC bypass.

The runtime package receipt must bind:

- current rendered SHA-256;
- current generation descriptor SHA-256 and transaction identity;
- Lua manifest SHA-256;
- the exact ordered set of 11 chunks and every SHA-256;
- bidirectional package/live file-set equality;
- stale, forbidden, missing, orphan, and hash-mismatch counts of zero.

Required regression coverage:

- default canonical runtime payload package succeeds without an RTC bundle;
- explicit RTC-certified package still invokes and requires the RTC guard;
- partial, mixed, or contradictory applicability fails before package write;
- manifest plus 11 chunks match live bidirectionally by SHA-256;
- forbidden monolith/stale bridge count is zero.

## 4. Current-route applicability and failure taxonomy

Every current-route validation is classified as one of:

- `current_product_required`: applies to current Iris source/rendered/runtime/package behavior and remains executable and fail-closed;
- `historical_optional_evidence`: preserves a historical authority/bundle assertion but is not selected as a current product gate; missing historical artifacts are never synthesized;
- `current_harness_required`: validates current behavior through disposable roots and must leave tracked mutation and residue at zero.

The live required-validation manifest retains historical rows and records their explicit applicability, authority basis paths, and current authority SHA binding. The runner filters only rows explicitly classified `historical_optional_evidence`; absence of classification remains required and fail-closed.

Required classification:

- historical RTC bundle checks and their bundle-only artifacts: `historical_optional_evidence`;
- obsolete source-authority reseal evidence: `historical_optional_evidence`;
- preserved assessment replay whose metric artifact is absent: `historical_optional_evidence`;
- package/runtime/exporter/current schema behavior: `current_product_required`;
- disposable checkout and cleanup behavior: `current_harness_required`.

## 5. Harness and current-schema corrections

- Temporary current-route attempts use a short external disposable root owned by the current test run.
- Existing roots fail-close; repository/live overlap, reparse traversal, and containment escape are rejected.
- Cleanup is retry-safe on Windows and verifies residue zero.
- Current-route tests never rewrite tracked staging evidence or the required-validation manifest.
- The current rendered test validates the adopted schema through the generation descriptor and source-pair hashes; it does not require obsolete `meta.overlay_path`.
- Default staging/historical exporter tests do not acquire RTC applicability unless they explicitly request RTC certification.

## 6. Test order

After implementation, run focused package/applicability, runner applicability, exporter, current schema, and cleanup regression suites. Then request Codex Reviewer review before broad validation.

Final validation runs only after the final implementation tree is committed:

1. exact Lua syntax validation;
2. canonical package command, exit 0;
3. package/live payload identity validation;
4. full current-route Run A, exit 0;
5. clean-checkout full current-route Run B, exit 0 with the same selected identity count;
6. runtime parity and consumer/display smoke;
7. tracked mutation, unrelated mutation, unresolved dependency, and disposable residue counts all zero.

Package and current-route outputs use fresh disposable roots. Only outputs created by the current run are removed.

## 7. Failure handling

- A current payload mismatch is a package/runtime product defect.
- A missing historical-only artifact is historical noncoverage, not a current defect.
- A Windows path, cleanup, or sandbox failure is a harness defect.
- An independently reproduced current RTC input failure may be recorded separately, but this plan does not create RTC or G6 debt from historical bundle failures.
- No failed test is silently deleted from the manifest and no evidence is synthesized to force PASS.

## 8. Completion claim

Only after every final validation gate passes, record:

`validated_naturalization_candidate_adopted_to_current_runtime_and_package`

The earlier runtime-only claim remains valid historical evidence but is not the full-problem completion claim.
