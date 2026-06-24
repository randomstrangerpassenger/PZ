# Round 3 Historical Artifact Reproducibility Audit

Generated: `2026-06-11T21:51:00+09:00`

## Executable Historical Route

The historical executable route is green:

| Route | Command | Result |
|---|---|---|
| unittest historical | `python -B Iris\_docs\round3\round3_run_contract_tests.py --class historical` | pass: 284 tests |
| pytest historical | `python -B -m pytest -q --round3-contract=historical Iris\build\description\v2\tests` | pass: 284 tests |

## Artifact Byte Reproducibility

Full historical artifact byte reproducibility is not green. The audit is
complete and fail-loud:

| Metric | Count |
|---|---:|
| artifact dependency rows | 281 |
| artifact-path signal rows | 271 |
| production mappings proven | 0 |
| production mappings unresolved | 281 |
| dependency mappings requiring keep/manual audit | 281 |
| byte-parity rows verified | 0 |

Reason: `round3_artifact_dependency_manifest.json` is a static
reference/signal inventory. It does not provide command-to-output production
maps or isolated regeneration recipes for all historical artifacts. Running
281 historical scripts directly against the live workspace would mutate
staging/output/runtime surfaces without a proven sandbox or byte-parity target.

## Closed Result

Historical executable reproducibility is proven for the separated test route.
Full historical artifact byte reproducibility remains a fail-loud unresolved
surface, not a silent pass.
