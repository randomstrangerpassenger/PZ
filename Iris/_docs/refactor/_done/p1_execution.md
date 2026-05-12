# Iris P1 Execution Note

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-01

## Scope

P1 closed the first architecture-boundary cleanup after P0.7 quarantine.

## P1-1 Offline Indexes

Runtime Lua no longer scans PZ recipe, moveable, or fixing objects during
`IrisMain.initialize()`.

Generated data artifacts:

| Artifact | Source | Count |
|---|---|---:|
| `Iris/media/lua/client/Iris/Data/IrisRecipeIndexData.lua` | `Iris/output/recipe_index.v2.4.json`, `Iris/output/dynamic_expr_catalog.v2.4.json` | 349 item role buckets |
| `Iris/media/lua/client/Iris/Data/IrisMoveablesIndexData.lua` | `lua/client/Moveables/ISMoveableDefinitions.lua`, `scripts/**/*.txt` | 23 registered items, 13 tag mappings |
| `Iris/media/lua/client/Iris/Data/IrisFixingIndexData.lua` | `scripts/fixing.txt`, `scripts/vehicles/vehiclesfixing.txt` | 20 fixer items |

Generator scripts:

- `Iris/build/description/v2/tools/build/build_iris_recipe_index_data.py`
- `Iris/build/description/v2/tools/build/build_iris_moveables_index_data.py`
- `Iris/build/description/v2/tools/build/build_iris_fixing_index_data.py`

Runtime wrappers kept the public API surface:

- `IrisRecipeIndex.getRoles()`
- `IrisRecipeIndex.matches()`
- `IrisRecipeIndex.inGetItemTypes()`
- `IrisMoveablesIndex.isItemIdRegistered()`
- `IrisMoveablesIndex.getMoveablesTag()`
- `IrisMoveablesIndex.tagIn()`
- `IrisFixingIndex.isFixer()`
- `IrisFixingIndex.roleEq()`

`IrisMain.initialize()` now only requires the three wrappers and logs
`precompiled data ready`; it no longer calls the three runtime `build()` paths.

## P1-2 Bullet Reload Compatibility Split

The vanilla bullet reload monkey patch was moved out of:

`Iris/media/lua/client/Iris/UI/Wiki/IrisContextMenu.lua`

New compat module:

`Iris/media/lua/client/Iris/Compat/IrisBulletReloadCompat.lua`

`IrisContextMenu.lua` now only resolves the clicked item and registers the Iris
wiki/browser menu entry. `IrisMain.initialize()` loads and installs the compat
module before registering the Iris context menu.

## Validation

Targeted generator tests:

`python -B -m unittest Iris.build.description.v2.tests.test_build_iris_index_data`

Result: 3 tests OK.

Full test suite:

`python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"`

Result: 315 tests OK.

Packaging verification:

`Iris/tools/package_iris.ps1 -Clean`

Result:

- package staging succeeded;
- manifest file count: 40;
- staged package root contains only `mod.info` and `media/`;
- forbidden roots including `_archive`, `_docs`, `build`, `input`, `output`,
  `lua`, and nested `Iris` were not included.

Boundary scan:

- no `IrisMain.initialize()` calls to `RecipeIndex.build()`,
  `MoveablesIndex.build()`, or `FixingIndex.build()`;
- no runtime calls to `getAllRecipes()`;
- no runtime calls to `ScriptManager.instance:getAllFixing()`;
- no vanilla bullet reload monkey patch remains in `IrisContextMenu.lua`.

The next in-game smoke marker list should expect:

- `[Iris:initialize] Step 2a: RecipeIndex precompiled data ready`
- `[Iris:initialize] Step 2b: MoveablesIndex precompiled data ready`
- `[Iris:initialize] Step 2c: FixingIndex precompiled data ready`
- `[Iris:initialize] Step 5b: BulletReloadCompat.install() success`
- `[Iris:initialize] Step 5c: hookContextMenu() success`
