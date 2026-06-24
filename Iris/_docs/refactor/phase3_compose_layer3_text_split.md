# Iris Refactor Phase 3 Compose Layer3 Text Split

Date: 2026-05-06

Historical source roadmap label: `docs/Iris/iris-refactoring-final-roadmap-v1.md`

This record starts Phase 3-4. The existing `compose_layer3_blocks.py` and
`compose_layer3_io.py` boundaries remain the authority for block rendering and
file I/O. New modules should only take responsibility that still lives inside
`compose_layer3_text.py`; they must not duplicate `blocks/io` behavior.

## First split

Added:

- `Iris/build/description/v2/tools/build/compose_layer3_identity.py`
- `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
- `Iris/build/description/v2/tools/build/compose_layer3_item.py`
- `Iris/build/description/v2/tools/build/compose_layer3_render.py`

Moved from `compose_layer3_text.py`:

- sentence finalization and Korean copula helpers
- identity core text rendering
- primary-use context derivation
- context containment checks
- body profile schema detection
- body profile resolution and precedence handling
- body-plan section selection and coverage quality candidate derivation
- legacy and v2 item composition helpers
- legacy and v2 render orchestration loops

Kept unchanged:

- public `build_rendered()` entrypoint remains in `compose_layer3_text.py`
- CLI modes and path contracts remain in `compose_layer3_text.py`
- `compose_layer3_blocks.py` remains the block renderer/repair helper boundary
- `compose_layer3_io.py` remains the description v2 I/O helper boundary

## Verification

- `python -B -m compileall -q Iris\build\description\v2\tools\build\compose_layer3_text.py Iris\build\description\v2\tools\build\compose_layer3_identity.py Iris\build\description\v2\tools\build\compose_layer3_body_profile.py Iris\build\description\v2\tools\build\compose_layer3_item.py Iris\build\description\v2\tools\build\compose_layer3_render.py`
- `python -B -m unittest Iris.build.description.v2.tests.test_build_iris_index_data`
- `python -B Iris\build\description\v2\tools\build\compose_layer3_text.py`
- `python -B -m Iris.build.description.v2.tools.build.compose_layer3_text`

All commands passed.

## Remaining Phase 3-4 scope

The requested internal module boundaries now exist while `build_rendered()`
remains the public entrypoint. A later cleanup can move stats/report assembly
out of the hub, but that is optional and should preserve the same direct script
and `python -m` execution checks.
