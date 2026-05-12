# T3-C Console Validation - 2026-05-12

## Source

- `C:/Users/MW/Zomboid/console.txt`
- Last write time observed: `2026-05-12 18:21:48`

## Result

The Iris refactor modules loaded without matching Iris require/runtime errors:

- `Iris/Util/IrisItemAccess.lua`
- `Iris/Util/IrisObjectAccess.lua`
- `Iris/Util/IrisTranslationResolver.lua`
- `Iris/UI/Browser/IrisBrowserTheme.lua`
- `Iris/Data/UseCaseDescriptions/RequirementsLookup.lua`

Boot logging used the cleaned format:

- `[Iris] Bootstrap start`
- `[Iris] IrisMain loaded`
- `[Iris] Bootstrap complete`

## T3-C Finding

Layer 3 data was still duplicated in the deployed mod:

- `Iris/Data/IrisLayer3Data.lua`
- `Iris/Data/IrisLayer3DataChunks.lua`
- `Iris/Data/IrisLayer3DataChunks/Chunk001.lua` through `Chunk011.lua`

Because Project Zomboid auto-loads Lua files under `media/lua/client`, this keeps
the monolith active even when the chunk manifest is present.

## Follow-up Change

`Iris/tools/package_iris.ps1` now removes
`media/lua/client/Iris/Data/IrisLayer3Data.lua` from the staged package after
copying `media/`, while preserving the chunk manifest and chunk files.

## Second Console Check - Historical Failed Run

Source:

- `C:/Users/MW/Zomboid/console.txt`
- Last write time observed: `2026-05-12 18:37:48`

Finding:

- `Iris/Data/IrisLayer3Data.lua` still loaded at line 1316.
- `Iris/Data/IrisLayer3DataChunks.lua` and `Chunk001.lua` through `Chunk011.lua`
  also loaded at lines 1317-1328.

Conclusion for that run:

- T3-C remained open for this run.
- The installed mod folder still contained the April 30 monolith file, even
  though the package output excludes it.
- This result is superseded by the final console check below.

Immediate local state after cleanup:

- `C:/Users/MW/Zomboid/mods/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`:
  removed.
- `IrisLayer3DataChunks.lua`: present.
- `IrisLayer3DataChunks/Chunk001.lua`: present.

## Workspace-Copy Correction

The user's validation flow deletes `C:/Users/MW/Zomboid/mods/Iris` and copies
the workspace `Iris` folder directly into the mod directory. That bypasses
package-only exclusions, so T3-C had to be enforced in the active workspace
layout as well as the packaging path.

Correction applied:

- The active workspace monolith
  `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua` was removed.
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua` was changed to load
  `Iris/Data/IrisLayer3DataChunks` and no longer require the monolith path.
- Runtime validation and closeout tooling now treats the chunk manifest and
  chunk files as the deployable authority, and treats the active monolith as
  absent from runtime deployment.

## Final Console Check

Source:

- `C:/Users/MW/Zomboid/Console.txt`
- Last write time observed: `2026-05-12 20:42:50`

Layer 3 runtime result:

- `Iris/Data/IrisLayer3Data.lua`: 0 loads.
- `Iris/Data/IrisLayer3DataChunks.lua`: 1 load at line 1372.
- `Iris/Data/IrisLayer3DataChunks/Chunk*.lua`: 11 loads at lines 1373-1383.
- Installed monolith path:
  `C:/Users/MW/Zomboid/mods/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`:
  absent.
- Installed chunk manifest:
  `C:/Users/MW/Zomboid/mods/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`:
  present.
- Installed chunk file count: 11.

Context menu compatibility result:

- `Iris/Compat/IrisContextMenuTextureCompat.lua`: 1 load at line 1365.
- `getWidthOrig`: 0 matches.
- `ISContextMenu.lua line # 475`: 0 matches.
- `STACK TRACE`: 0 matches.
- `java.lang.RuntimeException`: 0 matches.
- `Exception thrown`: 0 matches.

## Final Conclusion

T3-C is closed for the user's actual workspace-copy validation path. The active
runtime no longer deploys or loads the Layer 3 monolith alongside the chunk
manifest, and the companion CheatMenu context-menu regression observed during
validation is no longer present in `Console.txt`.
