# DVF VCS Tracking Policy Decisions Packet

> Status: compact ledger packet / not directly applied to `DECISIONS.md`

## Proposed Ledger Entry

### Iris DVF 3-3 - VCS tracking policy realignment

- Status: implemented / review handoff pending.
- Decision: DVF 3-3 artifact VCS tracking is role-based and remains orthogonal to artifact authority.
- Current read:
  - Current runtime deployable authority remains `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` plus `IrisLayer3DataChunks/*.lua`.
  - `export_dvf_3_3_lua_bridge.py` and `dvf_3_3_input_manifest.json` are tracked-required regeneration surfaces.
  - Round 3 current core remains 12 modules; `export_dvf_3_3_lua_bridge.py` is current-route regeneration tooling allowed for import by current route tests, not a current core module.
  - The current-route tooling allowlist is capped to one module in this round and guarded against convenience expansion.
  - `IrisLayer3Data.lua` monolith and `IrisDvfBridgeData.lua` bridge payload are forbidden on current-looking runtime/package/workspace surfaces.
  - Generated output is not broadly promoted to tracked status.
  - Quarantine evidence is retained only outside current-looking surfaces.
- Evidence:
  - Policy: `docs/dvf_vcs_tracking_policy.md`
  - Evidence root: `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/`
  - Guard: `Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py`
- Non-decision:
  - No release readiness, package release readiness, runtime rollout, successor cutover, manual in-game QA, or Stale Bridge Disposition sealed PASS.
