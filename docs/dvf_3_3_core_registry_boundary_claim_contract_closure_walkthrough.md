# DVF 3-3 Core / Registry Boundary Claim Contract Closure Walkthrough

> Status: current-session walkthrough / governance-only / no runtime-source-package mutation
> Round: `dvf_3_3_core_registry_boundary_claim_contract_closure`
> Primary evidence root: `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_claim_contract_closure/`
> Claim meaning authority: `docs/dvf_3_3_core_registry_boundary_claim_contract.md`

---

## 1. Starting Point

The predecessor `dvf_3_3_legacy_combined_route_axis_inventory_routing_preflight` had already separated the legacy combined current route into route / registry / runtime / publish / diagnostic axes.

The frozen read was:

- `current_route_required_validations.json` remains `legacy_combined_governance_route`.
- Legacy combined route PASS is not DVF Core PASS authority.
- The predecessor preflight is an input readpoint, not final boundary closure authority.

The unresolved gap for this session was claim vocabulary. The project still needed a machine-guarded contract proving that `DVF Core PASS`, `Registry Authority PASS`, `Registry Runtime Compatibility PASS`, `Publish Boundary PASS`, and `Legacy Combined Current Route PASS` cannot substitute for each other.

## 2. Implemented Scope

This session implemented the claim-boundary closure described by `docs/dvf_3_3_core_registry_boundary_claim_contract_closure_plan.md`.

The main additions were:

- `docs/dvf_3_3_core_registry_boundary_claim_contract.md`
- `docs/dvf_3_3_core_registry_boundary_claim_boundary.md`
- `docs/dvf_3_3_core_registry_boundary_claim_contract_ledger_packet.md`
- `docs/dvf_3_3_core_registry_boundary_claim_contract_closure_closeout.md`
- `Iris/build/description/v2/tools/build/dvf_3_3_core_registry_boundary_claim_contract_closure.py`
- `Iris/build/description/v2/tools/build/run_dvf_3_3_core_registry_boundary_claim_contract_closure.py`
- `Iris/build/description/v2/tools/build/validate_dvf_3_3_core_registry_boundary_claim_contract_closure.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_core_registry_boundary_claim_contract_closure.py`
- `Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_claim_contract_closure/`

`.gitignore` received narrow allowlist entries for only this round's new tool, focused test, and evidence root.

## 3. Claim Contract Result

The contract defines five claim classes with one owner axis each:

| Claim | Owner axis |
| --- | --- |
| `DVF Core PASS` | `dvf_core_body_compiler` |
| `Registry Authority PASS` | `registry_authority` |
| `Registry Runtime Compatibility PASS` | `registry_runtime_compatibility` |
| `Publish Boundary PASS` | `publish_boundary` |
| `Legacy Combined Current Route PASS` | `legacy_combined_governance_route` |

The default `DVF PASS` disposition is:

```text
dvf_pass_disposition=forbidden_standalone_current_claim
dvf_pass_standalone_current_claim_allowed=false
```

`legacy_alias_role_qualified` is not active under the default disposition. It can become active only under `legacy_alias_only` with a hash-bound owner record, which was not used in this session.

## 4. Machine Guard

The closure tool generates phase artifacts for:

- predecessor input hash binding and no-mutation proof
- isolated predecessor rerun under `phase0/predecessor_rerun/`
- roadmap attachment materialization
- claim contract document / JSON hash binding
- future-work routing matrix
- scan universe derivation
- lexical token-level overclaim scan
- negative fixture execution
- required-gate adoption decision
- final no-mutation and closeout report

The scanner class is intentionally limited:

```text
overclaim_scanner_class=lexical_token_level
semantic_overclaim_detection_scope=manual_review_or_independent_review_scope
```

This means it guards configured claim tokens and forbidden equivalence patterns. It does not claim complete semantic paraphrase detection.

## 5. Predecessor Freshness

The predecessor generator and validator were rerun with:

```powershell
$env:DVF_LEGACY_COMBINED_ROUTE_AXIS_INVENTORY_ROOT = "Iris\build\description\v2\staging\dvf_3_3_core_registry_boundary_claim_contract_closure\phase0\predecessor_rerun"
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_legacy_combined_route_axis_inventory.py --mode all
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_legacy_combined_route_axis_inventory.py --require-complete
```

Observed result:

- generator exit code: `0`
- validator exit code: `0`
- `predecessor_inventory_freshness_status=PASS`
- `predecessor_structural_freshness_status=PASS`
- `predecessor_rerun_root_override_supported=true`
- `predecessor_rerun_output_isolated=true`
- `predecessor_default_staging_root_write_count=0`
- `predecessor_input_artifact_mutation_count=0`

The regenerated predecessor semantic verdict remained `routing_preflight_blocked_pending_owner_adjudication` because of the known Non-Claims lexical false-positive class. This session accepted only the bounded row documented by the plan and recorded:

```text
predecessor_known_non_claim_false_positive_count=1
predecessor_known_non_claim_false_positive_status=PASS
owner_adjudication_scope=single_bounded_predecessor_non_claim_false_positive_row_only
owner_adjudication_does_not_generalize=true
```

## 6. Final Machine State

The final closure report is:

```text
Iris/build/description/v2/staging/dvf_3_3_core_registry_boundary_claim_contract_closure/phase6/final_boundary_split_closure_report.json
```

Key fields:

```text
status=machine_pass_governance_only
claim_boundary_split_complete=true
dvf_pass_disposition=forbidden_standalone_current_claim
legacy_combined_route_pass_is_dvf_core_pass=false
publish_boundary_pass_composition=conjunctive_all_components
partial_publish_boundary_bare_pass_allowed=false
required_gate_adopted=false
future_current_route_blocking_claimed=false
protected_surface_changed_count=0
undeclared_write_target_mutation_count=0
top_doc_sync_state=top_docs_updated_current_session_request_validated
top_doc_current_session_update_detected=true
top_doc_reference_coverage_status=PASS
independent_review_gate_status=not_claimed
owner_seal_status=not_claimed
canonical_seal_status=not_claimed
```

The forbidden overclaim scan reported:

```text
forbidden_overclaim_count=0
scan_universe_count=175
scan_universe_deduplication_status=PASS
inactive_exception_class_match_count=0
```

## 7. Validation Performed

The following exact commands were run in this session and exited with code `0`:

```powershell
uv run python -B Iris\build\description\v2\tools\build\run_dvf_3_3_core_registry_boundary_claim_contract_closure.py --mode all
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_core_registry_boundary_claim_contract_closure.py --require-complete
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_core_registry_boundary_claim_contract_closure.py"
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Observed validation results:

- closure runner: `PASS`
- closure validator: `PASS`
- focused unittest: `6 tests OK`
- current route: `127 tests OK`, `closure_enforced=true`
- Lua syntax: `Lua syntax validation OK: 188 files`

## 8. Non-Claims

This walkthrough does not claim:

- Registry implementation completion
- Registry Authority PASS completion
- Registry Runtime Compatibility PASS completion
- Publish Boundary PASS completion
- Runtime Payload Consumer Compatibility closure
- public text acceptance
- semantic quality acceptance
- package publication
- release / Workshop / B42 / deployment readiness
- manual QA
- source fact mutation
- rendered text rewrite
- Lua bridge export mutation
- runtime chunk mutation
- package payload mutation
- current-route required gate adoption
- independent review, owner seal, or canonical seal

## 9. Residual Boundary

The claim contract closure is complete for this round, but it is not yet a mandatory current-route required-validation gate:

```text
required_gate_adopted=false
future_current_route_blocking_claimed=false
```

Future work that wants current-route enforcement must open a separate adoption round or owner-approved manifest update.

Future DVF Core work must stay inside:

```text
facts / decisions / profile / body_plan -> rendered 3-3 body
```

It must not absorb current authority, staging evidence ownership, required-validation manifest ownership, seal/cutover, runtime/package guard, runtime consumer compatibility, public text acceptance, or release readiness responsibility.

## 10. Worktree Note

At closeout, `git status` also showed unrelated modified staging evidence files outside this round. They were not reverted or folded into this walkthrough. This session's declared mutation surface is limited to the top-doc updates (`DECISIONS.md`, `ROADMAP.md`, `ARCHITECTURE.md`), the new claim-contract docs, this walkthrough, new closure tool/runner/validator/test, this round's evidence root, and the narrow `.gitignore` allowlist entries.
