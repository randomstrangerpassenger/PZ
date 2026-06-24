# Round 2 Legacy Guard Baseline Report

Generated: 2026-06-10T15:46:56.459504+00:00

## Official Route

The official Change 0 baseline uses an in-scope validator code repair: `validate_legacy_active_silent_current_surface_guard.py` now enumerates `Iris` and `docs` with separate root-by-root `rg` calls instead of one internal multi-root `rg` command.

After Round 2 `.rgignore` introduction, the guard's internal `rg` calls use `--no-ignore` so staging/archive search-surface policy cannot shrink the validation surface.

The earlier normal run is superseded as comparison evidence only because it used the truncation-prone path.

## Known Finding Repair

- `Iris/build/ENTRYPOINTS.md:151` reworded from the legacy alias wording to `Historical execution build/generation manifest label`.
- `Iris/build/description/v2/tools/build/INVENTORY.md:302` reworded from the legacy alias wording to `historical execution manifest label`.

## Command

```powershell
python -B Iris\build\description\v2\tools\validate_legacy_active_silent_current_surface_guard.py --manifest Iris\build\description\v2\staging\compose_contract_migration\legacy_active_silent_current_surface_guard_round\phase1_manifest\current_surface_guard_referent_manifest.json --repo-root . --report .tmp\round2_guard_official_baseline.json
```

## Result

- status: `pass`
- occurrence_count: `10606`
- unclassified_occurrence_count: `0`
- hard_fail_current_label_occurrence_count: `0`
- manifest_error_count: `0`

This report is a guard baseline only. It is not runtime, package, release, Workshop, B42, or semantic-quality validation.
