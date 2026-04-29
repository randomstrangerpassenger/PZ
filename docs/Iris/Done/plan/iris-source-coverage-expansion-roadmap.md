# Iris Source Coverage Expansion Roadmap

_Last updated: 2026-03-28_

## Purpose

This document fixes the execution frame for the next Iris / DVF scale task:

- expand source-stage coverage beyond the current historical runtime batch
- reduce dependence on `identity_fallback`
- separate runtime availability work from semantic-quality work

It is subordinate to `Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`.

## Execution judgment

- Keep the ChatGPT 9-step logic as the reasoning spine, but compress execution into 3 blocks.
- Adopt the Claude-style `B / C` split as the first execution split, because it is an implementation-ready cut, not just an analysis taxonomy.
- Use the 6-axis priority matrix as the official scoring frame:
  - scale
  - path extensibility
  - semantic payoff
  - Layer 3 fit
  - implementation cost
  - fallback reduction
- Move the Wearable-cluster decision into Block A so roadmap scope is fixed before Phase B starts.
- Keep `direct_use` on explicit hold. It must not be planned as an expected path while current runtime usage remains `0`.
- Add the current `silent 75` as a required Block A audit target.

## Current repo baseline

The current repo already fixes a historical runtime milestone:

- runtime rows: `1050`
- active-displayable rows: `975`
- silent rows: `75`

The current historical runtime path distribution from `dvf_3_3_facts.full.jsonl` is:

- `identity_fallback`: `716`
- `cluster_summary`: `222`
- `role_fallback`: `112`
- `direct_use`: `0`

However, the repo still has baseline drift that must be frozen before coverage math is treated as contractual:

- `Iris/extraction_stats.json` says `items_total = 2281`
- a fresh read of `Iris/input/items_itemscript.json` currently yields `2285` `FullType` rows
- `Iris/lua/IrisData.lua` currently contains `1360` classified rows

This means earlier proposal counts such as `2282 / 1232 / 1323 / 1619 / 663 / 569` are not yet repo-locked. They remain provisional until Block A freezes `all_items_set`.

Using the current historical runtime set and the current `IrisData.lua` mapping, the provisional uncovered split is:

- classified but not yet in runtime (`B` group): `589`
- not in runtime and not in `IrisData`:
  - `642` if the `2281` baseline is frozen
  - `646` if the current `2285` input universe is frozen

Current provisional `B`-group distribution by top-level classification:

- `Consumable`: `344`
- `Literature`: `102`
- `Wearable`: `73`
- `Resource`: `56`
- `Combat`: `12`
- `Tool`: `2`

Current `identity_fallback` concentration already shows why Wearable needs an early scope decision:

- `Wearable`: `397`
- unclassified runtime rows: `144`
- `Consumable`: `85`
- `Combat`: `56`
- `Literature`: `14`
- `Resource`: `14`
- `Tool`: `6`

Current `silent 75` are all `role_fallback` failures, so they must be audited as a separate failure class, not mixed into generic uncovered counts.

## Block A: Data Freeze

Block A replaces the first 3 logical steps with one continuous baseline session.

Required outputs:

- `coverage_baseline_note`
- `all_items_set`
- `runtime_items_set`
- `uncovered_items_set`
- `uncovered_items_with_classification`
- `runtime_path_distribution`
- `runtime_path_by_classification`
- `wearable_preflight_decision`
- `silent_rows_note`

Block A rules:

- Freeze the canonical item universe before any matrix or Tier decision.
- Record the current baseline drift explicitly instead of hiding it:
  - `2281` from `extraction_stats.json`
  - `2285` from the current `items_itemscript.json` read
- Build the uncovered set only after that freeze.
- Project existing Iris classification onto the uncovered set before any phase ordering.
- Measure current runtime path distribution from real artifacts, not from plan prose.
- Audit why the `silent 75` stayed without final `primary_use`.
- Decide whether Wearable gets its own `B-W` phase before `B-1` starts.

## Block B: Analysis and Selection

Block B replaces the logical middle section with one execution-planning block.

Primary split:

- `B` group: already classified in `IrisData`, but still absent from runtime coverage
- `C` group: absent from both runtime coverage and current `IrisData`

Important rule:

- ChatGPT-style expansion types are kept as evaluation axes inside `B`, not as the top-level work buckets.

Provisional local `B` ordering from current repo data:

- `B-1`: `Consumable` (`344`)
- `B-2`: `Literature` (`102`)
- `B-3`: `Resource` (`56`)
- residual if Wearable stays merged: `87` (`Wearable 73 + Combat 12 + Tool 2`)

Wearable handling:

- If Block A says "dedicated Wearable lane is justified", promote it to `B-W` and remove it from residual work.
- If that happens, the residual phase shrinks to `Combat 12 + Tool 2`.
- If not, Wearable remains inside the residual phase, but that choice must be explicit and written down before `B-1`.

`C` group rule:

- `C` is a later source-expansion lane, not the first production target.
- Do not start `C` before Tier-1 `B` packages are defined.

## Block C: Source Package and Validation

Block C converts the selected Tier work into production-ready packages.

Required outputs:

- `tier1_source_packages`
- `validation_criteria_note`

Validation stays 3-axis:

- quantitative
- semantic
- structural

Existing phase-level operational checklists remain valid as an overlay, but the 3-axis frame is the top-level contract.

## Holds and prohibitions

- `direct_use` stays on hold until path distribution is re-measured after the `B`-group phases.
- Do not start with sentence polish before source coverage and path structure are expanded.
- Do not collapse `3-4` interaction detail into compressed `3-3` copy.
- Do not inflate coverage by treating `identity_fallback` growth as success.
- Do not use the `2281 / 2285` baseline drift as an excuse to stop the work.
- Do not process the uncovered universe item-by-item by hand as the main strategy.
