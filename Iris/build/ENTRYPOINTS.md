# Iris Build and Validation Entrypoints

Status: current human command literal owner

All commands require an explicit repository root and repository-external output roots. The installed wheel owns build and install implementations. Validation membership and verdict remain owned by `Iris/validation`; the CLI only delegates to that authority.

## Installed CLI

From an environment containing the exact `iris-tooling` wheel:

```powershell
iris-tooling --repository-root <repo> build classification --output-root <external-empty-root>
iris-tooling --repository-root <repo> build rightclick <arguments>
iris-tooling --repository-root <repo> build layer3 <arguments>
iris-tooling --repository-root <repo> build layer3 publish-tooltip-t1-owner
iris-tooling --repository-root <repo> build layer4 <arguments>
iris-tooling --repository-root <repo> build public-text <arguments>
iris-tooling --repository-root <repo> build tooltip-t1 --output-root <external-empty-root> --decision-contract-sha256 <sha256> --verify-invariants --layer2-menu-relation <external-relation-jsonl> --strict-production-handoff
iris-tooling --repository-root <repo> finalize tooltip-t1 --candidate-root <external-candidate-root> --candidate-run-receipt-sha256 <sha256> --run-a-orchestration-receipt <external-receipt> --run-b-orchestration-receipt <external-receipt> --comparator-receipt <external-receipt> --output-root <external-empty-root>
iris-tooling --repository-root <repo> build tooltip-t2 --handoff-root <current-successor-t1-root> --output-root <external-empty-run-root>
iris-tooling --repository-root <repo> finalize tooltip-t2 --run-a-root <external-run-a-root> --run-b-root <external-run-b-root> --output-root <external-empty-final-root> [--completion-metadata-json <json>]
iris-tooling --repository-root <repo> install classification --candidate-root <external-candidate-root> --manifest-sha256 <sha256>
iris-tooling --repository-root <repo> inspect current
```

`classification`, `rightclick`, `layer3`, `layer4`, and `public-text` remain compatibility aliases for their corresponding `build` targets. They are projections of the same package owners, not separate authorities. `tooltip-t1` is lifecycle-bound and has no legacy compatibility alias.

`tooltip-t1` reads only the owner-bound current Classification, pointer-selected Layer 3, current Layer 4 owner data, translation, Browser/Menu consumer, and Tooltip sources. It does not consume `Iris/build/baseline/**` as semantic authority. `--strict-production-handoff` requires the same-subject D2 relation and writes exactly `subject_binding.json`, `t2_handoff_input.jsonl`, `t2_handoff_manifest.json`, and `run_receipt.json` only when the T2-blocking correction set is empty. A blocked progression writes only the candidate run receipt and keeps subject binding, handoff input, and manifest absent.

`build layer3 publish-tooltip-t1-owner` follows the current Layer 3 English-localization producer and additionally publishes the exact single-core DVF fact identities and existing KO/EN primary-use surfaces consumed by Tooltip T1. It does not split rendered bodies, synthesize facts, or promote acquisition text to a core description; owner rows without one approved core fact remain corrections.

`finalize tooltip-t1` is a narrow post-gate binder, not a semantic producer. For a strict candidate it verifies blocker zero, `OPEN`, the 2,280 exact FullType set, subject/input/manifest hashes, exact subject, two successful canonical orchestration/inner result receipts, and their successful deterministic comparator receipt. It then byte-copies the three candidate handoff files and writes `axis_separated_final_closeout_record.json` to a repository-external empty root. Any failed gate, hash failure, or subject mismatch exits nonzero without a complete closeout.

The lifecycle-bound Tooltip T1 focused test command is:

```powershell
uv run --project .\Iris\tooling python -B -m pytest .\Iris\tooling\tests\test_tooltip_t1_contract.py .\Iris\tooling\tests\test_tooltip_t1_projection.py .\Iris\tooling\tests\test_tooltip_t1_audit.py -q
```

These six parameterized test families and the repository-external audit are lifecycle evidence. They are not added to regular validation membership by this adoption.

`tooltip-t2` remains the supported CLI token; its implementation is `iris_tooling.domains.tooltip_static_data_projection`. It consumes only the adopted strict T1 handoff with the approved S1 category/primary title successor. It preserves exact FullType, slot order, identities and explicit KO/EN strings in `IrisTooltipStaticData.lua`; every supported FullType has both arrays, including empty ones. It does not install runtime data or resolve owner semantics. The fixed lexical guard is defined in `Iris/_docs/authority/tooltip_t2/tooltip_t2_static_projection_contract.json`.

Each build writes Lua, `tooltip_t2_projection_manifest.json`, then `run_receipt.json`. Finalization checks distinct Run A/B roots, current input and exact implementation bindings, full coverage, zero violations and identical Lua/manifest bytes, then copies Run A and writes `tooltip_t2_closeout.json` last. Without completion metadata its state is `partial`, with pending checks listed in `unvalidated_but_in_scope`. A `complete` static-staging record additionally requires `focused_tests`, `installed_inspect`, `lua_syntax`, and `canonical_full_gate` metadata: each has the exact `command`, `exit_code: 0`, `subject: {commit, tree}`, and the run receipt's `artifacts` binding. These explicitly supplied execution results are not inferred from byte equality. They are retained in the closeout, not a separate proof package.

The dedicated T2 command (five function families, 18 collected cases; reader order includes three physical permutations) is:

```powershell
uv run --project .\Iris\tooling python -B -m pytest .\Iris\tooling\tests\test_tooltip_t2_projection.py .\Iris\tooling\tests\test_tooltip_t2_serialization.py .\Iris\tooling\tests\test_tooltip_t2_cli.py -q
```

T2 tests use the production decoder/model/serializer and independently bound temporary fixture repositories; there is no CLI admission bypass. The existing projection test checks the serialized manifest against the declared schema fields, types and bounds, plus KO/EN and line provenance invariants. Those test-local assertions are not a separate validator or validation authority; a schema hash alone is not a schema PASS. The full gate classifies these sources as `not_applicable_dedicated_route` and does not rerun them. Validation stops at offline static staging; actual PZ load, Alt/UI behavior and runtime/package adoption belong to T3.

## Receipt-bound full validation

T3's bounded standalone runtime harness (not a replacement for the full gate):

```powershell
uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py full
```

The same wrapper accepts `smoke` (payload/lookup) and `replacement` (reader/Alt
without Menu observations). Run replacement before an actual legacy deletion or
adapter change only. The canonical full gate already executes this wrapper in `full` mode; reuse that result and run it separately only for uncovered scope. It creates no receipts or
output files, has a 60-second subprocess timeout, and fails if Lua is missing.
Its test-local assertions do not constitute a canonical validator or new authority.
For the plan's once-per-input Menu comparison, append the explicitly admitted
`tooltip_t2_projection_manifest.json` path to `menu` (or to `full` only when its
additional runtime scope is required). The current route's manifest and product
hashes are checked before observation. The default test has no external input
dependency and does not include the offline Menu-to-T2 join.
`menu` selects only the Menu observation group;
it is not another mandatory run or an Alt runtime PASS.
The observation includes exact consumed text bytes, active modules, and absent
record reasons. The offline verdict also requires independently bound EN
producer/input/output/core-fact evidence for every required selected identity.
Without `--en-replay-root`, that evidence remains missing and cannot yield a
relation PASS. With an execution-authorized new leaf under the T3-D1 plan's
external output root, the existing producer and serializer reconstruct EN once,
compare every Index/chunk byte with current output, and connect approved
primary-use input to current source-bound core IDs before comparing Tooltip.
This is current deterministic derivability, not historical run provenance.

```powershell
uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py menu <admitted-tooltip-t2-manifest> [--en-replay-root <authorized-new-empty-leaf>] [--baseline-root <authorized-initial-snapshot-root>]
```

This option does not authorize external access: the execution prompt must allow
the plan's external output exception. There is no repository-local replay
fallback, live producer `main()` call, persisted evidence registry, or new gate.
The stdout relation report retains the exact initial selected ledger and its
resolved/retained/unresolved partition. Branch C preserves the initial required
scope; missing bodies remain unresolved, not legitimate silence. The optional
baseline root contains the saved initial `menu-before.txt`, `en-before` output,
and `owner-before.json`. Their bindings and the exact per-record body/identity
preservation are compared in the same final run, without a separate validator.
The focused admission cases stay inside the existing test method and can run
without the unrelated Alt suite:

```powershell
uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py BrowserStateSelectionSearchAcceptanceTest.test_browserdata_compatibility_and_logging_source_guards
```

The canonical CLI adapter invokes the repository-owned receipt-bound launcher:

```powershell
iris-tooling --repository-root <repo> validate full --commit <commit> --claim-id <claim-id> --environment-receipt <external-environment-receipt> --work-root <external-empty-work-root> --result-root <external-empty-result-root> --orchestration-receipt <external-new-orchestration-receipt>
```

The owning launcher is `Iris/validation/execution/invoke_repository_tests.ps1`; deterministic comparison is owned by `Iris/validation/execution/compare_repeated_test_runs.ps1`. Their parameters, validation membership, applicability, and verdict must not be reproduced in wrappers or documentation.

## Current and historical route selection

The exact read-only current denominator is:

```powershell
uv run python .\Iris\validation\execution\run_required_contract_tests.py --class current --list
```

Historical, diagnostic, and all repository-local executable selectors are retired.
The current runner rejects them before loading tests or materializing evidence.
Historical taxonomy and receipts remain records, not executable routes.

## Package output

Runtime packaging remains a separate repository-owned command:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot <external-package-root> -Clean -Zip -PackageApplicability current_runtime_payload
```

Direct execution of retired `Iris/build/description/v2/tools/build` copies is not a current command. Historical evidence may mention predecessor commands without re-adopting them.

## Tooltip Recipe opening variants (source presentation)

The fixed static tooltip dataset is not rewritten. This companion compiles the
Menu's approved structured QG recipe names into complete bilingual views; Alt
selects one view per opening. It is not a new fact source or T1/T2 closeout route.
Run from the repository root; only the explicitly named source asset is written:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = (Join-Path (Get-Location) 'Iris/tooling/src')
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.tmp/tooltip-recipe-uv-cache')
$env:UV_PYTHON_DOWNLOADS = 'never'
uv run python -m iris_tooling.domains.tooltip_static_data_projection.recipe_variants --repository-root . --output .\Iris\media\lua\client\Iris\Data\IrisTooltipRecipeVariants.lua
```

The current presentation exception and three user-approved missing-name
exclusions are recorded in the T3 plan's Recipe follow-up. An unexpected new
name/evidence/selection mismatch fails generation instead of inventing a label.
Copying source for this follow-up needs the companion, static lookup and Alt
renderer together; copying only the renderer is insufficient. Packaging is a
separate action and was not requested for this source-only follow-up.
