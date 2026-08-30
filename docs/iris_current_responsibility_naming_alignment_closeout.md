# Iris current responsibility naming — execution record

Date: 2026-08-30. Final state: **complete — naming and file placement only**.
Authority: `iris_current_responsibility_naming_alignment_plan.md`; owner decisions and
protected naming changes preapproved by the execution prompt. No independent review
or extra seal is required for this scope; none is credited.


## Final user-directed scope

The user explicitly ended validation and restricted the work to renaming and
corresponding file placement/reference updates. Under that final scope, N1–N7
are complete. N7's current locator and the immutable record already emitted by
the existing environment writer were copied from the task checkout into the
selected repository. Historical environment records and the old locator remain
intact. No additional tests, generation, packaging or in-game checks were run.

Earlier `partial`, `blocked`, pending validation and next-action sections below
are historical execution notes under the broader plan; they are no longer
completion conditions for the user's narrowed request. Existing mixed/lifecycle
and historical retain/defer decisions remain. This is not a claim that every
stage-named path in the repository was renamed.

The prior follow-up created a wheel, an external Python environment and its
existing-workflow receipt under `C:/Users/MW/PZ-N`. It did not execute canonical
full A/B/comparison or produce a new package. No further external input search
or recovery is required. Completion here does not claim production regeneration,
full-gate PASS, runtime certification, publication or deployment. The user subsequently
requested local main integration and a Git commit. The naming changes and preserved
Tooltip baseline are included; the unrelated DVF documentation folder is excluded.
The prior implementation snapshot is retained in ancestry. No remote push is requested.

## Scope and baseline

Base HEAD: `cc095398a273685f0e1c1216447d99927fe99316`. The existing Alt side-panel
layout and harness changes are the preserved working-tree baseline, not naming
changes. Existing additions in ARCHITECTURE, DECISIONS, ROADMAP and the T3 plan
are preserved. The unrelated `docs/dvf_b41_full_item_first_pass_2026-08-30/`
is excluded. No other module or external user directory is an input.

Baseline SHA-256:

| Asset | SHA-256 |
|---|---|
| Static Lua payload | `d9c88a437c60b49a631e214b577ab8e78a087435101e69d76c8b86e0c65aa10a` |
| Lookup | `e172d23d0c8ad7513fd97ac0a2e627f61d464fa13a54001e142848d4be17a22a` |
| Dirty Alt source | `63473fd5057d049b15c4db1040e17cc6a2948fe68609992e8f32eaa200bd3559` |
| Dirty runtime harness | `03edc33843454499040ffb7d32454ace94188fb626bf869445674bc0d3be1db3` |
| Required manifest | `ddd64d67d8f3132016ea418fbd751b3d921ff524622ce02118fa929d64f48e40` |

Read-only selection baseline is the exact sorted union of current/ok taxonomy IDs
and required IDs, excluding declared historical optional IDs: **103 identities**.
No baseline suite, generation or package was executed. No test source/node is renamed.
The source media tree and package selection rules are the package baseline;
older external packages are not assumed to contain the user's latest layout.

Scope scan: tracked filenames plus relevant source references under `Iris/media`,
`tooling`, `build`, `test`, `validation`, and individual live `_docs` readpoints;
root pytest discovery, package and syntax consumers; the four authority documents.
Historical `_docs/round3` and `_docs/refactor` records are classified by their
actual live reader, not by their containing directory. Ignored Iris inputs at
start: 154 Python bytecode files, 544 tooling-venv files and five tooling uv-cache
files. They are execution caches, not canonical source. Other temporary checkout
copies, `.git` internals, raw capsule objects and unrelated documents are not a
new source census. Capsule logical membership is read from its existing manifest.

## Scope lock and exact map

O1: dependency-driven C1/C3 preparation together; neither is adopted as a validated
successor before its required outcomes. O2: small module convention in `Iris/AGENTS.md`;
command ownership remains in ENTRYPOINTS. O3: no claim of solving all stage names.
The residual/current test families below are explicitly retained scope exceptions;
the user's preapproval covers this bounded disposition, not evidence of success.

All paths below are repository-relative. N3 maps each of `__init__.py`, `cli.py`,
`contract.py`, `projection.py`, `serialization.py` one-to-one within the directories.

| ID | Old path | Successor | Responsibility / consumers / binding |
|---|---|---|---|
| N1 | `Iris/media/lua/client/Iris/Data/IrisTooltipT2Lookup.lua` | `Iris/media/lua/client/Iris/Data/IrisTooltipStaticDataLookup.lua` | Internal first-use lookup; Alt and Lua harness require. No supported API entry promises the old require path; no external-consumer absence claim or new alias. V5/V6/V8. |
| N2 | `Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua` | `Iris/media/lua/client/Iris/Data/IrisTooltipStaticData.lua` | Generated KO/EN arrays; serializer LUA_NAME, lookup, wrapper hash and recursive package projection. Raw payload is unchanged; production fresh generation still required. V3/V5/V7/V8. |
| N3 | `Iris/tooling/src/iris_tooling/domains/tooltip_t2/` | `Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/` | Internal installed projection implementation; CLI dispatch and three dedicated tests. Both directory and qualified module change; CLI `tooltip-t2` stays supported. New wheel/environment binding required. V2/V3/V7/V9. |
| N4 | `Iris/test/lua/tooltip_t3_runtime_harness.lua` | `Iris/test/lua/tooltip_static_data_runtime_harness.lua` | Full runtime contract harness; Python subprocess path and menu_subject binding list. Existing dirty assertions, `next=nil`, marker and timeout retained. V6. |
| N5 | `Iris/_docs/round3/round3_run_contract_tests.py` | `Iris/validation/current_route/run_contract_tests.py` | Directory reclassification to validation; same parents[3] root, TEST_ROOT, current-only argparse and suite-lifetime projection. Audit, launcher-dependent readers and fixture runner paths move together. V4/V9. |
| N6 | `Iris/_docs/round3/current_route_required_validations.json` | `Iris/validation/current_route/required_validations.json` | Byte-preserving current binding projection. Original remains historical for pinned lifecycle readers. Current package, exporter, public-text consumer, audit, full A/B launchers and navigation read the successor. V1/V4/V8/V9. |
| Schema | `Iris/_docs/authority/tooltip_t2/tooltip_t2_projection_manifest.schema.json` | `Iris/_docs/authority/tooltip_static_data_projection/projection_manifest.schema.json` | Additive schema with new `$id` and only the Lua filename constraint changed; original preserved. Manifest schema_version/generator version and all other constraints unchanged. V3/V7. |

No semantic owner is transferred. N2 is currently a source payload move, **not**
an admitted production regeneration. N6 original is not a second current writer.
There is no global replacement of T1/T2, schema versions, content hashes or FullType.

## Retained / deferred ledger

| Paths / logical family | Disposition and reader |
|---|---|
| `tooltip_t1/{contract,models,projection,audit,cli}.py`, tests/fixtures and protected policy/authority | Mixed lifecycle/readiness and supporting contracts; keep original T1 identity. N3 imports its contract/model helpers. `admit()` still uses original CONTRACT_FILES against the historical T1 Git commit. No new handoff or weakened admission. |
| `tooltip_t1/d2.py`, `d5.py`, `d3_invariance.py`, `d4_invariance.py`; Layer3/4 `tooltip_t1_d3.py` / `tooltip_t1_d4.py` | Mixed or lifecycle-specific; defer extraction. d2 combines load_relation/HARNESS/PROJECTION_BUILDER with fixed-parent materialize/finalize; d5 combines exact identity/disposition helpers with fixed predecessor census/reconcile. Good whole-file functional name not established. |
| T2 dedicated `test_tooltip_t2_{projection,serialization,cli}.py`, `tooltip-t2`, JSON filenames and schema_version | Retained dedicated protocol/lifecycle identities; imports move, assertions/applicability do not. Not promoted to regular membership. |
| `_docs/round3/{round3_test_taxonomy,round3_active_core_closure,round3_pytest_source_classification,round3_full_discovery_denominator}.json` | Mixed historical records/live supporting projections; unchanged exact paths. Runner uses historical companions explicitly; pytest policy and full gate retain their existing reader. No directory-wide move. |
| `test_round3_*.py`, `runtime_payload_residual_seal_test_support.py`, `test_iris_residual_runtime_acceptance.py`, `Iris/test/*refactor*`, `validation/residual_refactor/**` | Current contracts coexist with lifecycle/evidence helpers. Only affected current references change. Pure recurring filenames in this group are bounded O3 scope exceptions, not solved naming targets. Structural/test-identity migration remains follow-up. |
| `validation/test_lightweighting/**`, `test_workflow_consolidation/**`, old build `*round*/*phase*/*migration*/*seal*/*refactor*` procedures | Historical/lifecycle investigation and fixtures retained; no restoration of executable historical selectors. Active package implementations are separate. These old procedures are not renamed or newly adopted. |
| N7 `responsibility_refactor_environment_current.json` and its immutable target | **Deferred/blocked**: only the existing environment receipt workflow may switch the locator; that requires a fresh external environment. No hand-written successor, source binding, or inherited PASS. |
| `_docs/refactor/core_refactor/phase0_supported_api_manifest.json` | Historical supported-API baseline with live acceptance reader; kept intact. IrisData, Browser, Wiki and legacy TooltipSummary remain supported as before. |
| Current capsule manifest/objects, historical archive/removal authorities, G5 chain | Retain original paths/bytes. None of N1–N6 is a capsule logical member. The 21 G5 compiler source paths do not intersect modified tooling files. No compiler identity successor required. |
| `v1/v2`, Layer 2/3/4, PhaseInput/Output/Runner, runtime session, `finalize` | Domain/version/execution semantics, not cosmetic stage names. |

## Dynamic resolution and documentation

This is task-local inventory, not a registry or a validator. Actual execution
results are shared across the applicable rows; no independent inventory gate exists.

| Origin / mechanism | Target set and disposition | Evidence |
|---|---|---|
| Lookup protected require; Alt require | Exactly successor Data/Lookup; C1 | V5/V6; V8 pending |
| Static harness DATA/READER, dofile, package.loaded/preload; browser/residual/metrics harness loaders | New static module names and repository media tree; C1 | V6; other full-gate harness consumers V9 pending |
| Browser Python wrapper PAYLOAD, subprocess and menu_subject | Successor payload hash and N4 path; Menu pointer-selected generation unchanged | V6; optional external Menu replay not run |
| CLI lazy import; five N3 relative imports; hatch package glob | `iris_tooling.domains.tooltip_static_data_projection.*`; C1 | V3; exact installed wheel V2 pending |
| T2 fixture Path.parents[3], temporary Git repo and schema copy | Original T1 contracts plus additive schema, fixture-only sibling output roots | V3 |
| N3 admit git show of T1 CONTRACT_FILES | Historical subject/path binding unchanged; C2 retained | V3 negative/admission cases; production input V7 pending |
| Runner parents[3], TEST_ROOT, importlib, unittest.loadTestsFromName | Same repository/test root and 103 identity set; C3 | V4 listing; actual full resolution V9 pending |
| Runner suite-lifetime IRIS_ROUND3_REQUIRED_VALIDATIONS_PROJECTION | Existing environment protocol retained; current successor manifest | V9 pending; no alias/protocol rewrite |
| Applicability/Git tests spec_from_file_location | New runner path; synthetic module labels retained | V9 pending |
| Audit AST walker, fixture copy/subprocess and launcher identity bindings | New runner and required manifest; taxonomy fixed; no path-check relaxation | V9 pending |
| Exporter / public-text / package defaults and fixture path composition | Successor required manifest; historical one-off readers keep baseline | V8/V9 pending |
| Package recursive media copy plus pointer-selected Layer3 generation | Baseline exact media members with N1/N2 substitution; one future package/install pair | V8 blocked |
| Environment writer/reader; capsule/archive lookup | N7 locator unchanged; historical logical paths unmodified | Deferred; V9 blocked |
| Root pytest / v2 conftest discovery | No test filename/node/class change; taxonomy/source policy unchanged | V9 blocked; no collected-count claim |

DECISIONS receives an additive current source readpoint; existing sealed entries,
hashes and statuses remain untouched. ARCHITECTURE updates the current runtime
chain and adds the current tooling/navigation mapping without rewriting dated
T1/T2 snapshots. ROADMAP adds the actual naming implementation/validation state;
earlier T3 completion remains about its old subject. ENTRYPOINTS changes current
paths and removes already-retired historical/diagnostic command examples.
The T3 plan itself is retained unchanged. These are Change 5 updates, not new
decision or validation authorities.

## Validation and ceiling

Final local execution results (all run after implementation, no intermediate suite):

| Evidence | Exact command / result |
|---|---|
| V3 dedicated projection route | `uv run --project .\Iris\tooling python -B -m pytest .\Iris\tooling\tests\test_tooltip_t2_projection.py .\Iris\tooling\tests\test_tooltip_t2_serialization.py .\Iris\tooling\tests\test_tooltip_t2_cli.py -q --basetemp=.tmp/n/t` — exit **0**, **18 passed**, 18.39 seconds. Existing editable environment, not a fresh installed-wheel PASS. |
| V4 listing | `uv run python .\Iris\validation\current_route\run_contract_tests.py --class current --list` — exit **0**; exact 103-ID baseline match, missing/extra **0**. Listing is not test execution. |
| V4 retired selectors | Same listing command with `--class historical`, `--class diagnostic`, `--class all`: each exit **2**, argparse `invalid choice`; expected rejection, not a gate PASS. |
| V5 syntax | `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` — exit **0**, **153 files**. Only repository `Iris/media/lua` existed; the default build/package root was absent. No external/install syntax claim. |
| V6 existing fallback | `uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py full` — exit **0**, `IRIS_TOOLTIP_T3_PASS mode=full exact_keys=2280 legacy_calls=0`. Menu source counts KO/EN 2084, L4 415. One fallback invocation because V9 cannot run; no extra smoke/replacement or external Menu replay. |
| V1 content/document comparison | Original payload SHA unchanged; lookup, dirty Alt and dirty harness exactly equal their pre-move text after only the declared module substitutions. Original and successor required manifest equal; the T3 plan unchanged. Existing DECISIONS/ROADMAP are exact preserved prefixes. No semantic equality inferred from mere counts. |
| Diff hygiene | `git -c core.safecrlf=false diff --check` — exit **0** after fixing one CRLF trailing-whitespace finding on the changed PAYLOAD declaration. This EOL-only fix followed V6; harness/runtime bytes and Python execution semantics did not change. No confidence rerun. |

UV cache, Python temporary roots and pytest fixtures were restricted to short
repository-local `.tmp/n` paths; sync/download/config discovery were disabled.
The running dedicated route was polled and completed normally; no long-running
process was left behind. Scratch code and outputs have no validator/authority status.
The final guarded PowerShell removal of `.tmp/n` was rejected by tool policy
before execution. It was not retried through another mechanism: this ignored
scratch directory remains, including the one-off editing script and baseline copies.
No new test function/file, validation framework, seal, receipt, manifest authority
or proof package was introduced; the schema is the plan-required filename contract.

V10 remains **partial**: listing and C1's exercised dynamic paths have evidence,
but installed producer, output-isolation/full-gate and package consumers have no
successor execution evidence. The retained denominator's
`exact_authority_reanchored.required_validations` is historical reanchoring metadata;
pytest enforcement reads its `enforcement` section, not that old locator.
Retired build procedures retaining old command literals are not current execution
dependencies, and this change does not make their replay supported.

Repository-external input/output
paths are not expressly authorized by this execution boundary. Consequently V2,
production V7, V8 and canonical V9 cannot be run by inventing sibling workspaces
or by weakening their external-root requirements. No external handoff, wheel,
environment, package, live game or save has been read or modified.

No fresh package means there is no exact package for the required KO/EN PZ smoke.
Existing T3 observations and receipts are not successor evidence. Final naming
adoption, canonical A/B/comparator and complete behavior preservation remain
unvalidated. No release, RTC, Publish, Workshop, deployment, architecture-redesign,
all-names-resolved, independent-review or sealed-closeout claim is made.

Ceiling: **validated** = the local commands and exact source comparisons above;
**unvalidated_but_in_scope** = V2, production V7/finalizer, V8 package/install,
V9 exact tracked A/B/comparator, remaining V10 consumers, N7 workflow and bounded
KO/EN PZ smoke; **out_of_scope** = mixed-file extraction, historical replay,
other modules, all-item/external-mod/performance QA and release/publication.
The source remains an uncommitted working-tree preparation, not an adopted
exact terminal subject. Owner preapproval was used for implementation/disposition;
it did not waive the external execution boundary or synthesize machine evidence.

Next required action is a concretely authorized external execution input/output
scope, followed by the existing fresh-wheel/environment, production A/B/finalizer,
package/install and canonical A/B/comparator workflows. N2's byte-preserved source
must still be regenerated directly under its successor name. Use the one resulting
package for the bounded PZ observation. No extra review/seal or validation-of-validation
gate is needed to resume.
