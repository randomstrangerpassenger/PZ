# Iris Authority Classification

Date: 2026-06-10

Status: current Iris authority classification guide.

This document closes Iris Round 1 at the classification level. It defines how
to read Iris files before future cleanup, move, or delete rounds. It does not
validate runtime behavior, package output, release readiness, Workshop
readiness, or in-game behavior.

## Authority Order

Use this order when files disagree:

1. `docs/Philosophy.md`
2. `docs/DECISIONS.md`
3. `docs/ARCHITECTURE.md`
4. `docs/ROADMAP.md`
5. `Iris/_docs/authority/iris_current_authority_manifest.json`
6. Current Iris contract files named by the manifest
7. Historical closeouts, round ledgers, staging artifacts, and generated output

The manifest is a navigation and cleanup-control artifact. It does not replace
the top project documents.

## Classification Vocabulary

### current

A current file is a live authority input for Iris work. It can define current
contracts, source facts, runtime source, validation commands, or build/package
baselines.

Default rule: do not delete, move, or rewrite a current file without an
approved focused plan and the validation named by the manifest entry.

### historical

A historical file is a predecessor, closeout, provenance note, prior plan, or
evidence record. It can explain why a current state exists, but it is not a
current readpoint unless a current file explicitly re-adopts it.

Default rule: do not use historical files as current authority. Moving them to
an archive is allowed only after references are ledgered and no current file
depends on their path.

### reproduction

A reproduction file is a build input, generated output, staging packet, test
fixture, package snapshot, baseline, log, or script family needed to recreate
or verify a result. It is not policy authority by existence alone.

Default rule: do not delete reproduction files by filename glob. Delete or move
requires proof that the file is not imported, path-executed, documented,
artifact-producing, or needed to reproduce a sealed result.

### stale

A stale file or path is superseded, deleted, or not a current authority input.
Its existence or old git history is not a reason to restore it.

Default rule: deleted `docs/Iris/**` files stay deleted unless a successor round
names a concrete file, a concrete reason, and a bounded correction or successor
scope.

## Deleted docs/Iris Policy

`docs/Iris/**` is classified as `stale` by default in the current worktree.

Round 1-A repaired live references that made deleted `docs/Iris/**` paths look
like current readpoints. Round 1 does not restore the deleted corpus.

Allowed exception:

- A future round may restore or recreate one specific `docs/Iris/**` file only
  when it declares a new input authority, an explicit successor/correction
  scope, and the reason the current manifest cannot cover the work.

Disallowed:

- restoring the corpus because paths are mentioned historically
- treating a deleted path as current because it appears in a closeout
- using deleted docs as release, runtime, package, or quality authority

## Current Baseline Anchors

Build contract:

- `Iris/build/ENTRYPOINTS.md`
- `Iris/build/build_import_contract.md`
- `Iris/_docs/refactor/phase1_active_manifest.md`
- `Iris/build/description/v2/tools/build/INVENTORY.md`

Runtime source:

- `Iris/media/lua/client/Iris/**`
- `Iris/media/lua/shared/translate/**`
- `Iris/media/textures/**`

Layer 3 deployable runtime data:

- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`

Package validation entrypoint:

- `Iris/tools/package_iris.ps1`

Package output:

- `Iris/build/package/**` is package output/reproduction state, not source
  authority by itself.

Description v2 current policy and source-data surface:

- `Iris/build/description/v2/*.md`
- `Iris/build/description/v2/data/**`
- `Iris/build/description/v2/acquisition/**`
- `Iris/build/description/v2/tools/common/**`
- `Iris/build/description/v2/tools/style/**`

Description v2 staging:

- `Iris/build/description/v2/staging/**` is reproduction/provenance by default.
  Staging artifacts do not become current authority unless a current manifest
  entry or current top document explicitly adopts them.

Legacy DVF predecessor overrides:

- `Iris/_docs/description_validation_contract.md` is a historical T-Gate/manual
  registry predecessor, not current DVF 3-3 authority.
- `Iris/_docs/layer3_authoring_guide.md` is a historical manual
  `layer3_registry.json` authoring guide, not current runtime payload or writer
  authority.

## Cleanup Decision Rules

Before a future delete/move round touches a file, it must answer:

1. Which manifest entry covers the path?
2. Is the classification `current`, `historical`, `reproduction`, or `stale`?
3. Does the entry require a reference ledger update?
4. Does the entry require import/path-execution/artifact proof?
5. Which validation command is required before claiming success?

No file may be deleted because it has an old name, lives under a staging tree,
or matches `build_*.py` / `report_*.py`. The local inventory explicitly forbids
filename-glob archive/delete decisions for
`Iris/build/description/v2/tools/build/*.py`.

## Manifest

The machine-readable manifest is:

- `Iris/_docs/authority/iris_current_authority_manifest.json`

Specific manifest entries override broader glob entries. If no entry matches,
the file is unclassified and must not be deleted or moved until the manifest is
extended.
