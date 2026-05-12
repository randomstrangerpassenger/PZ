# No-op API Deprecation Check - 2026-05-12

## Scope

- `Iris/media/lua/client/Iris/Data/IrisRecipeIndex.lua`
- `Iris/media/lua/client/Iris/Data/IrisMoveablesIndex.lua`
- `Iris/media/lua/client/Iris/Data/IrisFixingIndex.lua`

## Consumer Check

Command:

```powershell
rg -n "require\(.*Iris(Data/)?(Recipe|Moveables|Fixing)Index|require .*Iris(Data/)?(Recipe|Moveables|Fixing)Index|:build\(|\.build\(" Iris\media\lua\client Iris\build docs
```

Findings:

- `IrisMain.lua` loads the three precompiled index modules as ready modules and does not call their `build()` functions.
- Runtime `:build()` / `.build()` calls found in active Lua source are for `IrisBrowserData` and `IrisBrowserItemIndex`, not for `IrisRecipeIndex`, `IrisMoveablesIndex`, or `IrisFixingIndex`.
- The generated package snapshot still contains the same no-op build functions, but no active source consumer was found.

## Deprecation Marker

Each scoped index now exposes `build_deprecated = true` and marks `build()` with:

```lua
--- @deprecated Precompiled data is loaded when this module is required.
```

The function remains as a compatibility no-op returning `true`.
