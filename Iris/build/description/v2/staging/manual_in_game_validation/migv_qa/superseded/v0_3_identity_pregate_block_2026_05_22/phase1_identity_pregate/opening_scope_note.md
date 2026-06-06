# MIGV-QA Opening Scope Note

Status: blocked before manual in-game QA.

Selected identity-link mode:

```text
mode_b_prerequisite_deployable_authority_derivation_seal_round
```

Reason:

Current MIGV-QA v0.3 requires an opening-selected sealed evidence path/hash proving that the chunk deployable authority is content-equivalent to, or derived from, the sealed staged `body_plan` hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`.

No existing mode_a evidence satisfying that requirement was found in the current checkout. Historical top-doc decisions preserve staged/static and diagnostic hash claims, and the current runtime topology confirms chunked loading, but topology-only evidence is explicitly insufficient for mode_a.

Current local observations:

```text
chunk manifest present = true
chunk files = 11
chunk entries = 2105
chunk source distribution = composed_v2_preview 2084 / unadopted 21
current chunk publish distribution = exposed 1486 / internal_only 600 / missing 19
expected plan publish distribution = exposed 1467 / internal_only 617
current staged full_runtime hash = 9412BCD2316C02F357D1196F6B80EE0FCAEDC0F7B06C962240C16B3276F85277
expected sealed staged hash = 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
monolith IrisLayer3Data.lua exists = false
```

Default bounded baseline definition, for any later reopened manual QA:

```text
Iris-disabled vanilla behavior preservation
right-click entrypoint baseline leading to the Browser/Wiki path
```

This definition does not create a third Iris body display surface and does not duplicate Browser/Wiki validation under a new name.

Manual in-game validation is not started under this opening note.

Non-claims:

```text
No deployed closeout.
No manual in-game validation pass.
No ready_for_release.
No Workshop readiness.
No Tooltip validation or completion.
No canonical artifact regeneration.
No Branch A top-doc addenda.
```
