# DVF VCS Tracking Policy

> Status: subordinate VCS policy / implemented evidence surface
> Date: 2026-06-15
> Authority: `Philosophy.md` -> `DECISIONS.md` -> `ARCHITECTURE.md` -> `ROADMAP.md` -> this document

This document defines how DVF 3-3 artifacts are represented in Git. It does not promote or demote artifact authority. Runtime authority and VCS tracking status are separate axes.

## Current Boundary

Current runtime deployable authority remains:

```text
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua
```

`IrisLayer3Data.lua` monolith output and `IrisDvfBridgeData.lua` bridge output are not current runtime, package, source, or fallback authority.

## State Vocabulary

- `tracked`: normal Git index tracking is allowed.
- `tracked_required`: the path must be tracked for current regeneration or retained contract completeness.
- `ignored-reproducible`: the path may be ignored only after closure, two-run determinism, target fidelity, and manifest coverage pass.
- `reproduction-retained`: the path remains retained because reproducibility or route closure is not proven enough for ignore.
- `quarantine-retained`: stale or non-current evidence is retained outside runtime, package, and current-looking surfaces.
- `forbidden-current-looking`: the path or state is forbidden on current-looking surfaces regardless of authority claim.
- `selective-tracked-closeout-evidence`: selected round evidence may be tracked because review or closeout needs it.
- `ignored-generated-evidence`: generated evidence may remain ignored when closeout does not require tracking it.
- `reserved / hold`: no mutation until classification or policy decision is complete.
- `unknown_requires_review`: classification is unresolved and must be reviewed before mutation.

Artifact class and expected VCS state are different layers. For example, `forbidden_current_looking_stale` is an artifact class, while `forbidden-current-looking` is the expected VCS disposition for that class on current-looking paths.

## Artifact Classes

| Artifact class | Expected state | Rule |
|---|---|---|
| `source_input` | `tracked` or `tracked_required` | Source input is retained separately from fixture and generated output. |
| `fixture_non_authority` | `tracked` or `reproduction-retained` | Fixture material is not source authority or full current authority. |
| `regeneration-tooling` | `tracked_required` when consumed by current regeneration | Current regeneration tools must not be hidden by broad build ignores. |
| `current_regeneration_manifest` | `tracked_required` or explicit `reproduction-retained` | Manifest evidence must remain visible to clean checkout review. |
| `generated-intermediate` | `ignored-reproducible` only after closure and target fidelity, otherwise retained or local evidence | Determinism alone is not enough to ignore a generated artifact. |
| `runtime_deployable_authority` | `tracked` or separate retained verdict | Tracking status does not create authority status. |
| `staging_evidence` | `ignored-generated-evidence` by default | Selective tracking is allowed only for review/closeout evidence. |
| `historical_reproduction` | `reproduction-retained` or `tracked` | Historical route classification and VCS policy are separate. |
| `diagnostic_advisory` | `reserved / hold` or tracked only when a diagnostic route consumes it | Diagnostic material is not promoted by tracking policy. |
| `stale / quarantine-evidence` | `quarantine-retained` outside current-looking paths only | Quarantine is not package allowlist or current fallback. |
| `forbidden_current_looking_stale` | `forbidden-current-looking` | Must be absent from index, working tree, and package/workspace reachability. |
| `unknown_requires_review` | `reserved / hold` | Mutation is forbidden until reviewed. |

## Payload-Shape Fingerprint

Package and workspace scans must check more than filenames. The stale bridge / monolith payload-shape fingerprint includes:

- file family and format marker
- top-level Lua return or module shape
- known generated header or version marker when present
- `meta.stats` total and active count when present
- entry key set or chunk key range
- `entries_sha256` or equivalent normalized entry payload digest when present
- chunk manifest module prefix and chunk count when relevant

## Guard Surface

The focused guard route is:

```powershell
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_vcs_tracking_policy.py"
```

The guard evaluates expected predicates instead of treating raw `git check-ignore` or `rg` exit codes as pass/fail claims.

## Current-Route Tooling Exception Control

Round 3 current core remains 12 modules. `export_dvf_3_3_lua_bridge.py` is allowed only as `current_regeneration_tooling` for current-route tests that verify bridge export behavior.

This exception is deliberately narrow:

- It must not be counted as a current core module.
- The allowlist currently contains exactly one module.
- New modules must not be added as a convenience bypass for current core closure.
- Any expansion requires a separate reviewed scope that explains why the module is regeneration tooling rather than current core.
- The focused guard test fails if the core count changes, the allowlist grows, or the exporter is moved into current core.

## Non-Claims

This policy does not claim release readiness, package release readiness, runtime rollout, Workshop readiness, manual in-game validation, successor baseline identity, or Stale DVF Bridge Disposition sealed PASS.
