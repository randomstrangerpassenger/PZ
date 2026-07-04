# DVF 3-3 Legacy Combined Route Axis Inventory / Routing Preflight Walkthrough

Status: session walkthrough / independent DVF Core boundary-separation preflight / governance-only

## 1. Purpose

This session closed the routing preflight needed before separating pure DVF Core from the polluted current DVF governance surface.

The important architectural frame is that DVF Core is the pure 3-layer explanation block composition system. The current DVF route is not that pure core authority. It is a legacy combined governance route that currently mixes body compiler, current authority, runtime payload compatibility, publish boundary, stale predecessor guard, diagnostics, fixtures, and completion vocabulary checks.

Therefore this round is not a subordinate extension of the earlier current-route integrity closure. It is an independent boundary-separation readpoint. Its job is to create a machine-readable axis inventory so a later DVF Core / Registry boundary closure can decide which surfaces belong to which responsibility axis without physically splitting the manifest in this round.

## 2. Starting State

Before this round, the Iris current route worked through `Iris/_docs/round3/round3_run_contract_tests.py` consuming both:

- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/current_route_required_validations.json`

The active current core closure already distinguished body-composition-centered current core modules from bridge export tooling allowlists. However, the required-validation manifest still carried mixed responsibilities in a single governance route.

The preflight froze that route as:

```text
current_route_required_validations.json
= legacy_combined_governance_route
!= DVF Core PASS authority
```

## 3. Implemented Surfaces

The implementation added a dedicated DVF 3-3 inventory and validation toolchain:

- `Iris/build/description/v2/tools/build/dvf_3_3_legacy_combined_route_axis_inventory.py`
- `Iris/build/description/v2/tools/build/run_dvf_3_3_legacy_combined_route_axis_inventory.py`
- `Iris/build/description/v2/tools/build/validate_dvf_3_3_legacy_combined_route_axis_inventory.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_legacy_combined_route_axis_inventory.py`
- `docs/dvf_3_3_legacy_combined_route_axis_policy.md`

The generated evidence root is:

```text
Iris/build/description/v2/staging/dvf_3_3_legacy_combined_route_axis_inventory_routing_preflight/
```

`.gitignore` was updated with narrow allowlist exceptions for this tool/test/evidence surface. No existing current-route manifest, route runner, taxonomy, runtime chunk, bridge export, package output, or release surface was moved or physically split by this round.

## 4. Axis Contract

Every classified surface must map to exactly one primary axis from the fixed enum:

```text
dvf_core_body_compiler
registry_authority
registry_runtime_compatibility
publish_boundary
legacy_combined_governance_route
historical_predecessor_trace
diagnostic_or_fixture
```

`unknown` is not accepted as a passing classification. If a target cannot be classified, it becomes a blocker and must be recorded instead of silently passing.

The classification targets covered by this preflight are:

- required tests from `current_route_required_validations.json`
- required artifacts from `current_route_required_validations.json`
- current route runner claim surfaces
- active core closure module list
- bridge/export/package/runtime-related guard tests
- current-route/governance closeout documents

## 5. Generated Evidence

The minimum requested artifacts were produced:

- `legacy_combined_route_axis_inventory.json`
- `legacy_combined_route_axis_inventory.md`
- `routing_preflight_report.json`

Additional supporting reports were also generated, including required-test and required-artifact markdown slices, surface census files, guard inventories, active-core inventories, closeout claim scans, ambiguity reports, no-mutation reports, and validation reports.

The final routing preflight report recorded:

```text
status=PASS
semantic_verdict=routing_preflight_ready
blocker_count=0
current_route_union_test_count=127
required_test_count=48
required_artifact_count=93
ambiguity_queue_count=0
legacy_combined_required_item_without_route_reason_count=0
protected_surface_changed_count=0
legacy_combined_route_pass_is_dvf_core_pass=false
```

This means all current required tests and artifacts were classified for routing-preflight purposes, and the generated inventory is ready to be consumed by a later DVF Core boundary closure.

## 6. Validation Walkthrough

The inventory build and report generation passed:

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_legacy_combined_route_axis_inventory.py --mode all
```

Result: PASS, `blocker_count=0`, `semantic_verdict=routing_preflight_ready`.

The completeness validator passed:

```powershell
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_legacy_combined_route_axis_inventory.py --require-complete
```

Result: PASS, `error_count=0`.

The focused unit test passed:

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_legacy_combined_route_axis_inventory.py"
```

Result: PASS, 6 tests OK.

The current route still passed after the preflight work:

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
```

Result: PASS, 127 tests OK, closure enforced.

Runtime and package surfaces were checked for mutation:

```powershell
git diff -- Iris\media Iris\build\package
```

Result: empty diff.

Protected current-route input review found an existing dirty diff in `Iris/_docs/round3/round3_run_contract_tests.py` related to parent directory creation for `--out`. That edit was pre-existing in the worktree and was not introduced by this round. The generated no-mutation report for the DVF 3-3 preflight recorded `protected_surface_changed_count=0`.

## 7. Top-Document Updates

The session also updated the top-level governance docs so this work is represented as an independent boundary-separation preflight, not as a child item of the previous current-route integrity closure:

- `docs/DECISIONS.md` adds an independent DVF Core boundary separation preflight decision.
- `docs/ROADMAP.md` adds an independent Done item for the legacy combined route axis inventory.
- `docs/ARCHITECTURE.md` adds the DVF Core / Legacy Combined Route boundary block.

Those updates explicitly preserve the separation between:

- the legacy combined governance route
- DVF Core as the pure 3-layer explanation block composition system
- Registry authority
- Registry runtime compatibility
- Publish boundary responsibilities

## 8. What This Enables

The next DVF Core / Registry boundary closure can now consume a concrete axis inventory instead of trying to infer responsibility ownership from the mixed current route.

This preflight allows a later closure to ask focused questions:

- Which surfaces are pure DVF Core body compiler responsibilities?
- Which surfaces belong to Registry authority?
- Which surfaces belong to Registry runtime compatibility?
- Which surfaces are publish-boundary checks?
- Which surfaces are only legacy combined governance route obligations?
- Which surfaces are historical predecessor trace or diagnostic/fixture evidence?

Because the current route is frozen as a legacy combined governance route, the later boundary closure does not need to require a physical manifest split as part of this preflight.

## 9. Non-Claims

This session did not claim or perform:

- DVF Core boundary closure completion
- Registry Authority PASS revalidation
- Runtime Payload Consumer Compatibility closure
- Public Text Quality closure
- physical split of `current_route_required_validations.json`
- migration of required tests or required artifacts
- runner structure changes
- runtime chunk changes
- bridge export changes
- package or release readiness
- public text rewrite

The successful claim is narrower: the legacy combined route remains in place, its PASS is not DVF Core PASS, and a complete axis inventory is now available for future boundary separation work.

## 10. Consumer Freshness

Any later closure that consumes this inventory should rerun the DVF 3-3 generator and validator, or otherwise verify freshness, before treating the evidence as current. The inventory is designed as a boundary-separation input, not as a permanent replacement for the route authority itself.
