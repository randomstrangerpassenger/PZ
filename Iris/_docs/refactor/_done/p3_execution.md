# P3 Execution - Init/API Boilerplate Compression

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-01

## Completed

- Refactored `IrisMain.initialize()` from repeated load/build blocks into `INIT_MODULES` plus `runModuleSpec()`.
- Preserved per-step `debug`, `warn`, and `error` handling.
- Compressed `IrisAPI.ensureData()` with `requireOptional()`.
- Added `arrayContains()` and routed `hasTag()`, `hasOutcome()`, and `hasCapability()` through it.
- Added `Iris/Util/IrisRequire.lua` and routed runtime `pcall(require, ...)` usage through `safeRequire()`.

Remaining intentional direct require wrapper:

- `Iris/Util/IrisRequire.lua` contains the single shared `pcall(require, moduleName)` implementation.

## P3-5 Event Reduction

Runtime event trace from `C:\Users\MW\Zomboid\console.txt` on 2026-05-02:

```text
seq=1  event=OnGameBoot
seq=2  event=Iris.initialize state=enter initialized=false
seq=3  event=Iris.initialize state=complete
seq=4  event=OnMainMenuEnter
seq=5  event=OnCreatePlayer playerNum=0
seq=6  event=Iris.initialize state=enter initialized=true
seq=7  event=Iris.initialize state=skip_already_initialized
seq=8  event=OnGameStart
seq=9  event=Iris.initialize state=enter initialized=true
seq=10 event=Iris.initialize state=skip_already_initialized
```

Decision:

- Keep `OnGameBoot` as the sole initializer.
- Remove `OnCreatePlayer` and `OnGameStart` initialization hooks because both fired after initialization and only hit the idempotent skip path.
- Remove the debug-only `OnMainMenuEnter` hook.
- Remove the temporary `Iris:P3-5:EventTrace` marker after recording the order.

## Validation

Static test suite:

```text
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
Ran 315 tests in 3.436s
OK
```

Packaging:

```text
.\Iris\tools\package_iris.ps1 -Clean
Iris package staged: C:\Users\MW\Downloads\coding\PZ\Iris\build\package\Iris
Manifest written: C:\Users\MW\Downloads\coding\PZ\Iris\build\package\Iris.package_manifest.sha256.json
```

Package manifest:

- `file_count`: 42
- forbidden package roots: none
- staged package root contains only `media/` and `mod.info`

Note: the standalone `validate_interaction_cluster_phase_d_runtime.py` command still reports `blocked` against the existing staging bridge report because that stale report lacks `runtime_publish_state_counts`. The full test suite regenerates/uses the expected test artifacts and passes.
