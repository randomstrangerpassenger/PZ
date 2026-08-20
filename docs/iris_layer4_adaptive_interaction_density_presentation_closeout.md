# Iris Layer 4 adaptive interaction presentation closeout

> Historical-record notice (2026-08-21): this document remains the record of the earlier Gate 3 `BLOCKED` run. Its statements that owner policy or `preserve_legacy` was approved were based on an ineligible inferred approval and cannot authorize later implementation. The subsequent source-correction result is recorded separately in `docs/iris_layer4_gate3_source_migration_unblock_walkthrough.md`; this blocked closeout is not rewritten into a PASS closeout.

> Closeout state: `blocked`
>
> Selected path: Pre-seal / Gate 3 `BLOCKED`
>
> Contract report payload: `c70e882de05d7d866d16bc4e147abe05421436bb7b731873c238b3103832b367`

## Outcome

The owner-approved `L4-RAT-01`–`L4-RAT-07` policy and conservative `L4-RAT-08=preserve_legacy` tuple dispositions are bound in the staging decision packet and owner-policy seal. The fresh structured census does not pass Source migration readiness, so Change 2 and all later policy-dependent current implementation remain blocked as required by the plan.

This Layer 4 subject changed no current Lua runtime, current generated Layer 4 artifact, translation, PZ dev harness, or canonical `DECISIONS.md` / `ARCHITECTURE.md` / `ROADMAP.md` file. Concurrent or pre-existing changes to the three canonical documents appeared outside this subject during execution; the final no-current-mutation manifest lists them separately and does not attribute, inspect, or overwrite them.

## Fresh census

| Axis | Legacy/source | QG | Mapped | Legacy-only | QG-only |
|---|---:|---:|---:|---:|---:|
| Capability ↔ QG Right-click | 86 | 86 | 83 | 3 | 3 |
| Recipe ↔ QG Recipe | 794 | 791 | 791 | 3 | 0 |

Capability count equality does not provide identity parity. The legacy-only tuples are `Base.UnusableMetal`, `Base.UnusableWood`, and `Base.WeldingMask` with `can_scrap_moveables`; the QG-only tuples are `Base.BallPeenHammer/uc.action.construction`, `Base.GardenSaw/uc.action.wood_cutting`, and `Base.HammerStone/uc.action.construction`.

All Recipe-only tuples are `remove_battery` for `Base.HandTorch`, `Base.Rubberducky2`, and `Base.Torch`. They are exhaustively and disjointly classified as `qg_decided_no`. The approved `preserve_legacy` disposition leaves the producer denominator and raw Gate 3 result unchanged.

The installed density census remains `0=1216`, `1=300`, `2~8=99`, `9+=16`; maximum positive count is 40 for `Base.IronIngot`. Runtime chunk identity/order and line-count index mismatch counts are both zero.

## Validation

Required command for the selected path:

```powershell
uv run python -m pytest -q Iris/test/test_interaction_presentation_contract.py
```

Final result: `12 passed`, exit code `0`. Pytest emitted one non-failing cache-write warning for `.pytest_cache`; it does not affect the focused assertions or report output.

The V1 run generated the single raw contract report plus the path-selection, no-current-mutation, owner-seal, and isolated off-live stable-ID candidate files under `Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/`. The no-current-mutation assertion reports protected current mutation count `0`.

## Validation ceiling

- `validated`: fresh density/schema census; capability and Recipe structured crosswalks; Recipe failure-category union/disjointness; runtime chunk identity/order and line-count parity; deterministic replay; exact owner-policy/tuple binding; blocked-path selection; protected current mutation count zero.
- `out_of_scope`: QG coverage or decision changes, legacy fact correction, Layer 3 and item-page sufficiency reassessment, all-locale/resolution/mod/multiplayer/long-session/performance/release claims.
- `unvalidated_but_in_scope`: none for the selected blocked path.

`V2`–`V7`, PZ Kahlua/manual adaptive UI validation, disposable package projection, Layer 4 complete-generation installation, independent implementation review, and canonical promotion are `not_applicable(no_subject)` on this path. They are not PASS claims.

## Non-claims and next gate

This is not an adaptive presentation implementation, runtime/package validation, generated installation, canonical/sealed closeout, release readiness, or Workshop readiness claim. No mixed QG + legacy Recipe projection was created.

Full implementation can reopen only after external authority work makes both `capability_only == 0` and `recipe_only == 0`, followed by a fresh structured Gate 3 census. Owner approval alone does not bypass those raw identity conditions.
