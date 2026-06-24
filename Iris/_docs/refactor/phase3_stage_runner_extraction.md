# Iris Refactor Phase 3 Stage Runner Extraction

Date: 2026-05-06

Historical source roadmap label: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

This record starts Phase 3-2 after Phase 3-1 centralized the active
root/pipeline JSON I/O call sites.

## Common helper

The shared stage orchestration helper is:

- `Iris/build/tools/common/stage_runner.py`

Current API:

- `StageRunner.announce(code, title)`
- `StageRunner.run(action, failed=None, abort_message=None)`
- `StageRunner.save_json(path, data, indent=2, trailing_newline=False, on_saved=None)`

The helper intentionally handles only scheduling/logging skeleton concerns.
It does not classify evidence, merge decisions, or reinterpret recipe and
right-click tracks as the same semantic source.

## Migrated usage

| Script | Migration | Verification |
|---|---|---|
| `Iris/build/rightclick_evidence_pipeline.py` | Phase S/C/D/U/F abort handling now goes through `StageRunner.run`; JSON artifact writes now go through `StageRunner.save_json`; track-specific phase functions remain local | direct execution covered by cross-track fixture, `python -m Iris.build.rightclick_evidence_pipeline --v24` PASS |
| `Iris/build/recipe_evidence_pipeline.py` | R0/R1/R2/R3/RQ/R4/R5/R6 stage headings now go through `StageRunner.announce`; JSON artifact writes now go through `StageRunner.save_json`; recipe phase functions remain local | direct execution covered by cross-track fixture, `python -m Iris.build.recipe_evidence_pipeline` PASS |

## Cross-track fixture

Added:

- `Iris/build/tests/test_evidence_pipeline_cross_track.py`

The fixture hashes right-click outputs before running the recipe pipeline and
asserts they do not change. It then hashes recipe outputs before running the
right-click v2.4 pipeline and asserts they do not change. This verifies the
roadmap rule that one track's stage movement must not mutate the other track's
artifacts.

## Verification

- `python -B -m compileall -q Iris\build\tools\common\stage_runner.py Iris\build\recipe_evidence_pipeline.py Iris\build\rightclick_evidence_pipeline.py Iris\build\tests\test_evidence_pipeline_cross_track.py`
- `python -B -m unittest Iris.build.tests.test_evidence_pipeline_cross_track`
- `python -B -m Iris.build.recipe_evidence_pipeline`
- `python -B -m Iris.build.rightclick_evidence_pipeline --v24`

All commands passed.

## Remaining Phase 3-2 scope

The first extraction deliberately stops before classifier/decision hooks.
Further extraction can move summary boilerplate into common code, but only with
the same cross-track fixture in place and without mixing recipe evidence
authority with right-click evidence authority. Hash semantics remain track-local
for now because the two pipelines currently print hashes with different
serialization choices.
