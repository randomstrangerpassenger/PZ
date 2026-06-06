# Iris DVF 3-3 Structural Signal Scope Split Seal Round Walkthrough

Closeout state: `blocked_missing_current_readpoint_inventory`.

The round preserved the structural signal / `ACQ_DOMINANT` / publish-mutation lane split, but did not complete the full structural signal current readpoint seal because the required physical anchor artifact pair is absent in the current checkout.

Expected anchor:

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.jsonl
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/phase4_artifacts/body_plan_structural_reclassification.2105.summary.json
```

Expected hashes:

```text
row sha256     = 6e84bb2f9622b79493473631d391a01c857c04ddbea869993a99856283ecb6d9
summary sha256 = 8b6b7b34ba4c5de9bf6df6d8bcdfeacc6ec86ebda9f0c0b883672177d7b508cf
```

Filesystem result:

```text
row artifact exists = false
summary artifact exists = false
selected anchor = none
```

Preserved boundary:

```text
Structural signal remains observer/readpoint only.
ACQ_DOMINANT remains future separate current-baseline remeasurement only.
The source expansion 이후 precondition remains intact.
ACQ_DOMINANT is not a current publish mutation candidate.
Fresh measurement alone does not reopen publish writer authority.
```

Validation performed:

```text
python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"
exit code = 0, observed tests = 398

powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
exit code = 0, observed files = 183
```

Non-claims:

```text
no ACQ_DOMINANT remeasurement
no ACQ_DOMINANT publish candidate opening
no source expansion
no publish mutation review
no quality_state mutation
no publish_state mutation
no rendered text regeneration
no Lua bridge regeneration
no runtime chunk regeneration
no runtime rollout
no deployed closeout
no manual in-game QA pass
no Workshop readiness
no ready_for_release
no runtime equivalence
```
