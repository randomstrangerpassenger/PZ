# Iris Build Import and Execution Contract

Status: Phase 3 prerequisite

Date: 2026-05-05

Historical source roadmap label:
`docs/Iris/iris-refactoring-final-roadmap-v1.md`.

Current readpoint for this contract is the inline content below plus
`docs/DECISIONS.md` and `docs/ROADMAP.md`, not the archived Iris docs path.

This contract is the gate before introducing shared build helpers under
`Iris/build/tools/common`.

## Supported execution forms

The primary supported form is direct script execution from the repository root:

- `python -B Iris/build/<entrypoint>.py`
- `python -B Iris/build/tools/pipeline/<script>.py`
- targeted test execution for known active tests, for example
  `python -B -m unittest Iris.build.description.v2.tests.test_build_iris_index_data`

Namespace module execution may work for scripts that already satisfy it, for
example:

- `python -B -m Iris.build.rightclick_evidence_pipeline --v24`
- `python -B -m Iris.build.tools.pipeline.build_action_requirement_index`

However, direct script execution remains the compatibility baseline for Phase 3.

## Not supported yet

- `python -B -m unittest discover -s Iris/build/tests -p "test_*.py"`
- Arbitrary CWD execution
- Requiring every root or pipeline script to support `python -m`
- Adding package marker files solely to force dotted imports

The root `Iris/build/tests` folder contains script-style tests that call
`sys.exit()` at import time. Phase 10 (Change 10) resolves this roadmap item:
the discovery policy is consolidated inline in this contract and script-style
conversion is deferred (low-risk-only).

Historical Phase 10 source note labels:

- `docs/Iris/phase10_test_discovery_compatibility_note.md`
- `docs/Iris/phase10_validation_matrix.md`

## Pytest discovery contract

Phase 3-6 adds `pytest.ini` at the repository root. The default pytest
discovery scope is intentionally narrower than the full `test_*.py` inventory:

- `Iris/build/description/v2/tests`
- `Iris/build/tests`

`Iris/build/tests/conftest.py` limits pytest collection in the root build test
folder to unittest-compatible files only. Script-style regression checks in
that folder remain direct execution targets until they are converted away from
import-time work and `sys.exit()`.

Current pytest-active root build test:

- `Iris/build/tests/test_evidence_pipeline_cross_track.py`

Compatibility commands remain valid and are the required fallback when pytest
is not installed:

- `python -B -m unittest Iris.build.description.v2.tests.test_build_iris_index_data`
- `python -B -m unittest Iris.build.tests.test_evidence_pipeline_cross_track`

## Common helper import rule

Common build helpers live under:

- `Iris/build/tools/common/`

Root `Iris/build/*.py` scripts may import common helpers as:

```python
from tools.common.io import load_json, write_json
```

Pipeline scripts under `Iris/build/tools/pipeline/` must preserve direct path
execution by adding `Iris/build` to `sys.path` before importing common helpers:

```python
BUILD_DIR = Path(__file__).resolve().parents[2]
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

from tools.common.io import load_json, write_json
```

This keeps the existing no-`__init__.py` namespace-package behavior intact while
allowing shared helpers to be introduced incrementally.

## Helper behavior requirements

JSON helpers must preserve existing build artifact behavior unless a caller
explicitly opts into a difference:

- UTF-8 read/write
- `ensure_ascii=False`
- stable optional `sort_keys`
- caller-selected indentation
- trailing newline for generated JSON files by default
- parent directory creation for writes

## Phase 3 migration rule

Migrate one active script or tightly related script family at a time. Each
migration must verify:

- direct script execution
- module execution if the script already supported it
- relevant quality gate or focused test

## Phase 1 readpoint update (2026-06-07)

Historical amendment label:
`docs/Iris/Iris_Refactoring_Plan.md` (Draft v6.0) Change 1/Change 3.
Additive; the contract above is unchanged.

- Direct script execution from the repository root **remains the compatibility
  baseline**. conflict 14.2 (standardize on `python -m` vs preserve direct
  execution) is **deferred** to a user decision and is the Phase 3 entry gate.
  Until 14.2 is resolved, compose `try/except ImportError` dance removal is
  forbidden and Phase 3 is limited to introducing a leaf path helper.
- Phase 3 cleanup targets (sealed baselines; historical baseline metrics label:
  `docs/Iris/phase1_baseline_metrics.md`): `sys.path.insert` occurrences = 134,
  `ROOT =` bootstrap occurrences = 254, compose `except ImportError` = 5 - all
  measured under `Iris/build/description/v2/tools/build/`.
- Historical single readpoint label:
  `docs/Iris/phase1_inventory_readpoint.md`.

## Change 3 update (2026-06-07): package form adopted (compose core)

conflict 14.2 is now **resolved = package form** - this supersedes the
"deferred / direct-execution baseline" note just above **for the migrated
surface**. Change 3 migrated the compose core:

- `compose_layer3_*.py` use package-internal **relative imports**
  (`from .compose_layer3_io import ...`); the `try/except ImportError` fallback
  was removed (`compose_except_import_count == 0`). They load only inside the
  `tools.build` package - `python -m tools.build.compose_layer3_text` or
  `from tools.build.compose_layer3_text import ...`, no longer bare
  `python compose_layer3_text.py`.
- `style.normalizer` is now `from tools.style.normalizer import ...`
  (the `sys.path.insert(parent.parent)` bootstrap was removed in item/render).
- A leaf path helper `Iris/build/description/v2/tools/common/paths.py`
  (description-v2 tree) exposes `V2_ROOT`/`BUILD_ROOT`; `compose_layer3_text`
  imports `V2_ROOT as ROOT`.
- Caller import lines updated to the package path in
  `build_body_role_full_preview.py`, `build_layer3_body_plan_v2_preview.py`,
  `build_adapter_native_body_plan_metadata_migration.py`,
  `build_runtime_payload_enum_rename_scope_round.py`.

Metrics: `compose_except_import_count` 5->0; `root_bootstrap_count` 254->253;
`syspath_insert_count` 134->132. Legacy/frozen reproduction scripts retain their
direct-execution bootstrap and migrate incrementally. Note the repository has
**two distinct `tools` trees**: `Iris/build/tools` (root scripts: io, versions,
pipeline) and `Iris/build/description/v2/tools` (description-v2: build, style,
common).

Historical compose import note label:
`docs/Iris/phase3_compose_import_contract_note.md`.

## Round 3 test-contract route (2026-06-11)

Round 3 separates the description-v2 `tools.build` test contract from the
historical reproduction test inventory without moving tests or changing pytest
discovery. The default current route is the manifest runner below:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

Current-route constraints:

- The current route contains 44 unittest cases.
- `tools.build` imports are limited to the 12-module active core closure in
  `Iris/_docs/round3/round3_active_core_closure.json`.
- `test_compose_layer3_text_overlay.py` is current by manual audit promotion
  because it imports only the active composer and validates current overlay
  behavior.

Historical reproduction and diagnostic tests remain runnable, but they are not
the default current contract route:

```powershell
python -B Iris\_docs\round3\round3_run_contract_tests.py --class historical
python -B Iris\_docs\round3\round3_run_contract_tests.py --class diagnostic
```

Boundary guard:

```powershell
python -B Iris\_docs\round3\round3_boundary_guard.py --self-test
```

This is a D1 routing decision only. It does not approve pytest routing changes,
physical test moves, archive/delete disposition, or historical preservation
policy. D2/D3 remain separate gates.

## Round 3 disposition and closeout note (2026-06-11)

D2 was approved only for non-destructive disposition evidence. The resulting
manifest keeps all 281 measured `tools/build` scripts:

- 12 `keep_current_core`
- 173 `keep_historical_reproduction`
- 95 `keep_diagnostic_advisory`
- 1 `keep_manifest_only`
- 0 archive/delete eligible

D3 selected `pass_required` for the sealed historical route. The historical
route currently passes with 284 unittest cases. This preserves the measured
historical executable route, but it is not a claim of full historical artifact
reproducibility, release readiness, runtime equivalence, pytest parity, or
deletion safety.

Closeout artifact:
`Iris/_docs/round3/round3_closeout_report.md`.

## Round 3 pytest default route update (2026-06-11)

After pytest was installed and verified (`pytest 9.0.3`), the default pytest
route was narrowed to the current contract:

```powershell
python -B -m pytest -q
```

Result: `45 passed, 363 deselected, 5 subtests passed`.

The 45 default pytest cases are the 44 description-v2 current-contract tests
plus `Iris/build/tests/test_evidence_pipeline_cross_track.py`. Historical and
diagnostic description-v2 tests are explicit routes:

```powershell
python -B -m pytest -q --round3-contract=historical Iris\build\description\v2\tests
python -B -m pytest -q --round3-contract=diagnostic Iris\build\description\v2\tests
```

Route evidence:
`Iris/_docs/round3/round3_pytest_route_report.md`.
