# Iris DVF 3-3 Diagnostic-only Resolver Compatibility Guard Round Walkthrough

> 상태: closed walkthrough  
> 기준일: 2026-05-17

## What Changed

The v2 body profile resolver now has an explicit resolver authority mode.

- Default mode keeps `selected_role` as native resolver authority.
- Default mode rejects legacy compatibility fallback authority with `DEFAULT_RESOLVER_REJECTED_LEGACY_COMPAT_LABEL`.
- Diagnostic resolver mode can exercise the legacy mapping explicitly.
- Diagnostic CLI output paths must stay under the diagnostic staging root.

## Code Surface

- `Iris/build/description/v2/tools/build/compose_layer3_body_profile.py`
- `Iris/build/description/v2/tools/build/compose_layer3_item.py`
- `Iris/build/description/v2/tools/build/compose_layer3_render.py`
- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`
- `Iris/build/description/v2/tools/build/report_diagnostic_resolver_guard_round.py`

## Validation

Command:

```powershell
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
```

Observed result:

```text
Ran 386 tests in 3.527s
OK
```

Round-local report:

```powershell
python -B Iris\build\description\v2\tools\build\report_diagnostic_resolver_guard_round.py
```

## Results

- `rendered_delta_count = 0` for current v2 preview text in the guard/no-guard comparison scope.
- `default_path_legacy_fallback_reach_count = 0`.
- `selected_role_precedence_default_influence_count = 264`.
- `selected_role_target_default_influence_count = 642`.
- Lua runtime git diff surface is empty.
- Chunk manifest and chunk files are unchanged.

## Non-Claims

This walkthrough does not declare selected-role removal, complete-removal cleanup, adapter removal, runtime Lua regeneration, manual in-game QA, deployed closeout, Workshop release, or `ready_for_release`.
