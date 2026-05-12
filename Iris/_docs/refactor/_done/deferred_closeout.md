# Deferred Item Closeout

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-02

This document records the code implementations used to close the roadmap's
remaining deferred items after the P7 pass.

## `pcall` policy redefinition

Status: implemented.

Runtime protected calls now route through:

- `Iris/Util/IrisProtectedCall.lua`

Direct runtime `pcall` usage under `media/lua/client/Iris` was migrated to this
shared boundary. `IrisRequire.safeRequire` also delegates to
`IrisProtectedCall.require`, so optional module loading and engine/UI/data
probes can be tightened from one place later.

## P5-1 generated data split

Status: implemented as Lua chunk externalization.

The large generated `IrisUseCaseDescriptions.lua` module is now a runtime
facade. The data rows are emitted into chunk modules under:

- `Iris/Data/UseCaseDescriptions/ChunkNNN.lua`

The public require path remains unchanged:

- `Iris/Data/IrisUseCaseDescriptions`

This avoids adding a runtime JSON parser dependency while still completing the
actual data externalization work in code.

## Namespace integration

Status: implemented.

The IrisDesc implementation moved from:

- `Pulse/Iris/Logic/IrisDesc/*`

to:

- `Iris/Logic/IrisDesc/*`

The old `Pulse/Iris/Logic/IrisDesc/*` files now act as compatibility wrappers.
New Iris code should require `Iris/Logic/IrisDesc/*`.

## Browser requirement color/text policy

Status: implemented.

Requirement state colors and learned-label behavior now live in:

- `Iris/UI/Browser/IrisRequirementPolicy.lua`

The existing visual behavior is preserved.

## `IrisMapIcon.lua` hardcoded coordinates

Status: implemented.

The Iris Browser standalone button position moved to:

- `IrisConfig.MAP_ICON_BUTTON`

The default values preserve the previous UI position.
