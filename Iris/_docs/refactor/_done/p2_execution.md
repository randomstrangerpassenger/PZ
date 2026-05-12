# P2 Execution - Logger and Runtime Print Reduction

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-01

## Scope

P2 introduced a runtime logger and moved noisy diagnostics behind `DEBUG=false`.

Completed:

- Added `Iris/media/lua/client/Iris/Util/IrisLogger.lua`.
- Set release defaults in `Iris/media/lua/client/Iris/IrisConfig.lua`:
  - `IrisConfig.DEBUG = false`
  - `IrisConfig.RUN_TESTS_ON_START = false`
- Updated `Pulse/Iris/Logic/IrisDesc/Logger.lua` to delegate `debug/info/warn/error` to `IrisLogger`.
- Replaced runtime diagnostic `print(...)` calls in Iris/Pulse client Lua modules with logger calls.
- Kept warnings and errors as `warn(...)` / `error(...)` paths.
- Moved the unused `debugTranslationSystem()` diagnostic block out of runtime media into `Iris/_dev/IrisTranslationDebug.lua`.

Remaining direct `print(...)` calls under runtime media are intentional:

- `Iris/Util/IrisLogger.lua`: logger sink.
- `Iris/IrisMain.lua`: fallback warn/error when the logger cannot load.
- `Pulse/Iris/Logic/IrisDesc/Logger.lua`: fallback warn/error when `IrisLogger` cannot load.

## Validation

Static test suite:

```text
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
Ran 315 tests in 3.583s
OK
```

Packaging:

```text
.\Iris\tools\package_iris.ps1 -Clean
Iris package staged: C:\Users\MW\Downloads\coding\PZ\Iris\build\package\Iris
Manifest written: C:\Users\MW\Downloads\coding\PZ\Iris\build\package\Iris.package_manifest.sha256.json
```

Package manifest:

- `file_count`: 41
- forbidden package roots: none
- staged package root contains only `media/` and `mod.info`

Runtime acceptance still requires a game launch smoke test to confirm `DEBUG=false` suppresses debug logs while warnings/errors remain visible.
