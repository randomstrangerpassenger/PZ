# Iris Agent Bootstrap

Read `docs/Philosophy.md` first, followed by `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`. Use those four documents as the Iris planning and implementation bootstrap, applying progressive disclosure to task-relevant sections.

## Current path naming

Name durable modules, tests, and generated assets for their current responsibility.
Use one domain term across languages: `TooltipStaticData` / `tooltip_static_data`,
with role suffixes such as `Lookup`, `projection`, and `runtime_harness`.
Move a producer, its output names, and direct/dynamic consumers together.
Read the implementation's inputs, operations, outputs, and callers before naming
it. A task directory or phase label is not a substitute for a file's responsibility.
Validation code uses `execution`, `source_analysis`, `artifacts`, `baseline`,
`scenarios`, and `test_coverage`; each filename must still describe its own work.
Keep protocol versions, supported public names, historical evidence, and lifecycle
identities intact; defer mixed responsibilities instead of disguising them with
a generic name. Command literals remain owned by `Iris/build/ENTRYPOINTS.md`.
