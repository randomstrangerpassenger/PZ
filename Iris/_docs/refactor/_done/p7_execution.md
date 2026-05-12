# P7 Execution Notes

Archived under `_done` by the Phase 1 v1.4 refactor doc split.

Date: 2026-05-02

## Scope completed

- Inventoried Python scripts in `Iris/build`.
- Created `Iris/build/ENTRYPOINTS.md` to document allowed root scripts.
- Created `Iris/build/tools/oneshots/`.
- Moved low-risk historical analyzers and one-off mutation helpers into
  `Iris/build/tools/oneshots/`.
- Created `Iris/build/tools/pipeline/`.
- Moved root pipeline helpers and legacy build utilities into
  `Iris/build/tools/pipeline/`.
- Created `Iris/build/tests/`.
- Moved root test scripts into `Iris/build/tests/`.
- Created `Iris/build/data/v2.4/`.
- Moved root JSON/SHA policy artifacts into `Iris/build/data/v2.4/`.
- Updated build scripts, quality gates, tests, and one-shot tools to read policy
  data from `Iris/build/data/v2.4/`.
- Split `Iris/build/description/v2/tools/build/compose_layer3_text.py`:
  - `compose_layer3_blocks.py`: legacy block rendering and repair helpers.
  - `compose_layer3_io.py`: JSON/JSONL and hash IO helpers.
- Patched relocated scripts that depended on their old `__file__` location:
  - `extract_merge_candidates.py`
  - `fix_expected_diff_for_v2_5.py`
  - `verify_tagnames.py`
  - pipeline helpers under `tools/pipeline/`
  - root tests under `tests/`

## Root state

After this pass, root-level Python scripts are limited to the documented
entrypoints in `Iris/build/ENTRYPOINTS.md`.

Root-level JSON/SHA artifacts were removed from `Iris/build` and versioned under
`Iris/build/data/v2.4/`.

`compose_layer3_text.py` remains the public import hub and CLI entrypoint, but
IO and legacy block responsibilities now live in dedicated modules.

## Validation results

- `python -B -m compileall -q Iris\build\tools\pipeline Iris\build\tests Iris\build\tools\oneshots`: PASS.
- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`: PASS, 319 tests.
- `python -B Iris\build\test_require_render.py`: PASS.
- `python -B Iris\build\tests\test_fail_loud_coverage.py`: PASS.
- `python -B Iris\build\tests\test_wearable_6f.py`: PASS.
- `python -B Iris\build\tools\pipeline\build_recipe_nav_registry.py`: PASS.
- `python -B Iris\build\tools\pipeline\build_recipe_requirements_index.py`: PASS.
- `python -B Iris\build\tools\pipeline\build_usecases_by_fulltype.py`: PASS.
- `python -B Iris\build\quality_gates.py --update-sha`: PASS; refreshed frozen SHA after accepted P5 description output change.
- `python -B Iris\build\quality_gates.py`: PASS.
- `python -B -m unittest Iris.build.description.v2.tests.test_compose_layer3_text_v2`: PASS, 7 tests.
- `python -B Iris\build\description_generator.py`: PASS.
- `python -B Iris\build\convert_descriptions_to_lua.py`: PASS.
- `.\Iris\tools\package_iris.ps1 -Clean`: PASS.
