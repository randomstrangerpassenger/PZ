# DVF 3-3 vNext Guard Seal Contract

Status: single-writer guard contract for the delta disposition guard-seal round.

The guard seal is implemented as a single orchestrator over existing evidence and route reports. It does not create a second current authority and does not copy staging payloads into live paths.

## Guard Matrix

- Fixture-as-Authority Guard
- Monolith Re-entry Guard
- Staging Direct Promotion Guard
- Parity-Missing Guard
- Disposition Coverage Guard
- Unapproved Delta Guard
- Single-Authority Guard
- Legacy Vocabulary Guard

All guards are fail-loud. Historical, diagnostic, and staging surfaces may remain only with explicit non-current context and current-route non-reachability.

## Forbidden Current Path Patterns

- `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`
- `media/lua/shared/Iris/IrisDvfBridgeData.lua`
- `Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua`
- direct promotion from `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/`
- direct promotion from `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/`

Approved delta manifests are manifest/index-only. They are not rendered, Lua bridge, chunk payloads, release readiness, or cutover authorization.
