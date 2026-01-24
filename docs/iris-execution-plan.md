# Iris Execution Plan (Doc-Driven, Guarded)

Goal
- Make documents the single source of truth (SoT).
- Force runtime and CI to fail if the SoT changes or is violated.
- Prevent implementation drift and silent interpretation.

Scope
- Inputs are only the 4 fixed JSON files.
- Rules are generated only from the SoT docs.
- Classification is add-only with no inference or scoring.

SoT Documents (changing these must break the pipeline)
- `schema/iris-input-schema-v0.2-final.json`
- `policy/iris-evidence-allowlist-v0.2.md`
- `tables/` (six Evidence Table md files)
- `dsl/iris-rule-dsl-spec-v1_1.md`

Directory Layout
```
schema/      # JSON schema for the 4 inputs
policy/      # allowlist and guard policy
tables/      # evidence tables (md)
dsl/         # DSL spec and related docs
engine/      # parsers, validators, evaluators, reporters
generated/   # build outputs only; manual edits must fail
```

Execution Flow (fixed)
```
4 JSON -> Schema Gate -> Collector -> Evidence IR -> Rulegen -> AST Guard -> Eval -> Reports
```

Phase 0 - Repo Skeleton and Generated Guard
Goal
- Lock the repo layout and prevent manual edits in `generated/`.
Tasks
- Create required directories.
- Add CI step that regenerates `generated/` and fails if diffs exist.
- Add manifest or hash file for `generated/` to detect manual edits.
Outputs
- `generated/.regen-manifest.json` (or similar)
- CI job: `regen_check`
Gate
- Any manual edit in `generated/` causes failure.

Phase 1 - Input Loader and Schema Gate
Goal
- Ensure only the 4 JSON inputs are accepted and fully validated.
Tasks
- Implement loader with fixed file names and paths.
- Validate against `schema/iris-input-schema-v0.2-final.json`.
- Enforce `additionalProperties: false`.
Outputs
- `validation_report.json`
Gate
- Any schema violation stops the pipeline.

Phase 2 - Allowlist AST Guard
Goal
- Reject forbidden operations before evaluation.
Tasks
- Implement `Guard.validateRuleAst(ast)` with hard rejects:
  - No numeric comparisons.
  - No bare `exists` except documented exceptions.
  - Tags must be explicit strings from Item Script only.
  - `TwoHandWeapon` is presence-only.
  - MoveablesTag and ItemScript Tags are separate namespaces.
Outputs
- `guard_reject_samples.md` or `guard_reject_samples.json`
Gate
- Forbidden rule shapes fail fast.

Phase 3 - Evidence Table (md) to IR
Goal
- Make md tables executable and rigid.
Tasks
- Strict parser for the 6 md tables.
- Produce IR with a fixed schema.
Outputs
- `generated/evidence_ir.json`
- `generated/evidence_ir_schema.json`
Gate
- Any md format drift breaks parsing.

Phase 4 - Collector (Evidence Only)
Goal
- Normalize evidence without inference.
Tasks
- Extract evidence from:
  - `items_itemscript.json`
  - `recipes_index_full.json`
  - `fixing_fixers.json`
  - `moveables_tooldefs.json`
- Record missing data as incomplete only.
Outputs
- `evidence_snapshot.json` (debug/spot-check)
Gate
- Policy decides whether incompletes are fatal.

Phase 5 - Rulegen + Evaluation
Goal
- Rules are generated, never hand-authored.
Tasks
- Generate rules from `dsl/`, `tables/`, and `policy/`.
- Evaluate in fixed order:
  - Tool -> Combat -> Consumable -> Resource -> Literature -> Wearable
- Add-only tagging, no removal.
- Emit audit metadata per tag.
Outputs
- `tags_by_fulltype.json`
- `classification_report.json`
Gate
- Missing audit fields fail.

Phase 6 - Manual Overrides (Only Where Allowed)
Goal
- Allow manual tags only when `AutoClassifyAllowed=false`.
Tasks
- Accept a manual overrides file as a strict map.
- Mark `source=manual` in audit.
Outputs
- `overrides_manual.json`
Gate
- Any override for auto-allowed tags fails.

Phase 7 - Tests and Regression Gates
Goal
- Detect doc-implementation drift early.
Tasks
- Schema gate tests (additionalProperties, enum, type).
- AST reject tests (forbidden ops, mixed namespaces).
- Evidence parser regression tests (md format).
- Golden set tests for a curated item list.
- Statistics report (unclassified, multi-tag, distribution).
Outputs
- `tests/` coverage for gates
- `stats_report.json`
Gate
- Any mismatch or regression fails CI.

Acceptance Criteria
- Changing any SoT doc causes a build or runtime failure until regenerated.
- Only 4 JSON inputs are accepted.
- No rule files can be hand-edited without CI failure.
- Every tag has an evidence key and rule reference.
- Manual overrides are limited to explicitly blocked auto-tags.

Notes
- Version upgrades (e.g., DSL v1.2) are out of scope.
- No extra normalization outside schema rules.
