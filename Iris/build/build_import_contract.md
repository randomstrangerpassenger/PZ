# Iris Build Import and Execution Contract

Status: Phase 3 prerequisite

Date: 2026-05-05

Source roadmap: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

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
`sys.exit()` at import time. Pytest/unittest discovery for that folder is a
separate roadmap item.

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
