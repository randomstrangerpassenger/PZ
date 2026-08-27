# Iris build-validation execution/current-authority optimization closeout

Status: implementation and machine validation complete; plan-process closeout partial pending owner disposition of missing W0 admission evidence

## Bound subjects

- product S0: `e6310737a99873e2c58f3f399de77ef97473f39f` / tree `fa58a95445a75308d06b24ac8515ea4d0789ca0f`
- documentation-only plan carrier: `e0d22781e0595abfd07da82150219d39969f6d4a` / tree `202ddfdb33c98caefa81a67d755f7fe844258238`
- final package-source implementation subject: `c334ee97f0c01fb826309a6fb5388e99bde518d7` / tree `d66ac0b0261ef6001c9e902e9b63c80a8750f37b`
- machine-validation environment subject: `7a6e8ef9e9c29d5986872b08bdbeded5f086b536` / tree `44ac4a756fe6b32cf6cebf29951be4b954bda94a`; direct parent is the final package-source subject and its commit changes only the versioned environment authority record and current locator
- carrier parent and only S0-relative path: exact S0 / `docs/iris_build_validation_execution_current_authority_optimization_plan.md`
- W0 current-route listing: exit `0`, 103 Round3 routing identities, LF-normalized SHA-256 `3406301be19d3cf5c1491b450b90938cf68371d7284a4d8e7ce61bd7917b9b95`
- W0 authority manifest: `Iris/_docs/authority/iris_current_authority_manifest.json`, S0 blob `47624dc14dae148e988f60c1a5877324c30122e9`, raw SHA-256 `38f1bdc90c1ff8d3b17bbc71c3ecb184bc4239a572aa90b8ad84cad011933901`
- W0 required-validation projection: raw SHA-256 `ddd64d67d8f3132016ea418fbd751b3d921ff524622ce02118fa929d64f48e40`
- W0 census: `C:/Users/MW/i/iris-build-validation-optimization-e0d22781/w0/w0_census.json`, SHA-256 `d4e72b9747d39b75ac12b02832500761cf82d1f88b2af115b43eaeee800fe702`
- external custody owner: this optimization implementation; explicit root `C:/Users/MW/i/iris-build-validation-optimization-e0d22781`; repository/source-checkout descendant: false; tracked source mutation allowed: false

## W0 admission evidence status

Read-only inspection of `C:/Users/MW/i/iris-build-validation-optimization-e0d22781/w0` and its exact parent custody root found no pre-implementation artifact that combines W0 elapsed time, Wave 1–3 projected time, total ≤120 minutes, explicit `ADMIT`, and plan-carrier/exact-base binding. `w0_census.json` records candidates and custody only; it is not admission evidence. No retroactive artifact or exemption was created, and observed outcome timestamps are not used to reconstruct the missing decision.

```text
W0_ADMISSION_EVIDENCE_MISSING

The implementation outcome completed within a bounded observed timeline,
but the plan-required pre-implementation elapsed/projected-time ADMIT
artifact was not preserved.

Observed timestamps are outcome evidence only and do not reconstruct
the missing pre-admission decision.
```

- implementation: complete
- package-bound machine terminal: PASS
- independent Reviewer: PASS, actionable finding `0`
- product/runtime/Lua mutation: `0`
- W0 pre-implementation admission: unresolved
- overall plan-process: partial pending owner disposition

Reviewer PASS does not replace the missing admission evidence.

The exact G5 0013→0014→0015 paths, Git blobs, raw SHA-256 values, schemas, and PASS statuses matched the plan at W0, and successors 0013 through 0016 remain byte-immutable. Successor 0017 corrects the current closure from 19 to 21 paths by adding the plan-required identity owner `Iris/tooling/src/iris_tooling/build/naturalization_compiler_identity.py` and the production dependency `Iris/tooling/src/iris_tooling/execution.py`, removing no path. It binds basis commit `d103cf7815b98793b718361b65dbdac3e2aadfaa` / tree `dbdcf31a277537d1b0ec1f0508723506459146c4`, aggregate `61238620a841bc635169d5f254ceab9279f4b71d9231fdc2cd660c7b3afdb6ab`, and committed raw SHA-256 `8e5261338f7b4518b03b331df8da6ddabce15842b5188be995a39421c8c38e5f`. The current required-evidence list retains 0016 and then 0017; no 0018 was created because the later retention-list correction changed no compiler closure bytes.

## Candidate disposition

| ID | Before | Terminal disposition | Result |
|---|---|---|---|
| OPT-001 typed execution/result boundary | public phase/build/validation/CLI projections used unrelated dict/tuple/exit forms | `adopt_and_implement` | generic phase I/O, canonical semantic result, volatile envelope, issue/artifact, machine projection, and explicit legacy adapters added |
| OPT-002 StageRunner duplication | two live runner implementations | `merge_into_current_owner` | both adapters converge on thin package-owned `PhaseRunner`; domain I/O stays outside the runner |
| OPT-003 current-output seed | 2 materializations × 3 producers = 6 invocations | `adopt_and_implement` | one staging build, completeness/content identity check, immutable final publish, and five case-local clones = 3 producer invocations |
| OPT-004 repeated helper candidates | no additional candidate exceeded one subprocess, two reads, 64 KiB, one owner/hop, or one live-copy threshold after OPT-002 | `below_materiality_threshold` | no new helper authority introduced |
| OPT-005 same-name predecessor copies | 31 substantive basenames / 33 concrete predecessor files: 5 exact, 28 diverged | `retire_predecessor_copy` | 33 archived and physically retired; different-name exact duplicate count remained 0 |
| OPT-006 command/readpoint fragmentation | four current command/explanation owners and no static route index | `merge_into_current_owner` | command literals converge on `ENTRYPOINTS.md`; `IRIS_CURRENT.md`, agent bootstrap, and one static route index added |
| OPT-007 protected historical/reproduction corpus | historical records and nonmatching predecessor tools | `retain_protected_reproduction` | excluded from live-copy denominator; no current import or command authority retained |

Terminal counters: `unsupported_retention=0`, `remaining_eligible_optimization=0`, `unimplemented_optimization=0`, `unmeasured_defer=0`, `undispositioned_candidate=0`.

## Archive and current-route measurements

- predecessor denominator: `32 distinct basename intersections - 1 non-substantive __init__.py = 31 substantive distinct basenames`; nested D16 adds one extra concrete predecessor copy for each of `run_dvf_3_3_korean_prose_naturalization.py` and `validate_dvf_3_3_korean_prose_naturalization.py`, so `31 + 2 = 33 concrete predecessor files`
- classification: `5 exact + 28 diverged`; substantive distinct basename live implementation intersection `31 → 0`; concrete predecessor files `33 → 0`
- the two nested D16 copies are not neutral protected fixtures, and 33 is not an arbitrary expansion of the 31-basename scope
- predecessor archive manifest: `C:/Users/MW/i/iris-build-validation-optimization-e0d22781/archive/archive_manifest.json`, 33 entries, SHA-256 `87c2c7a56670b9efe6c87c5775ab933a9d10dbe272908b60083e22031a6402d3`
- all-entry path/size/SHA verification: PASS
- representative restore: largest diverged retired entry, `public_text_quality_acceptance.py`, byte identity PASS
- human command literal owners: `4 → 1`
- current authority explanation owners: `4 → 1`
- current readpoint maximum route hop: `4 → 1`
- default current-context files: `5 → 6`
- default current-context tracked bytes: `170,476 → 149,600`
- current readpoint: 31 lines / 2152 bytes; route index: 1891 bytes
- live same-name predecessor authority duplicates: `33 → 0`
- different-name exact duplicates: `0 → 0`
- current predecessor import/execution references on guarded surfaces: `0`
- current document disposition counters: all `0`; the frozen `Iris/_docs/round3/round3_active_core_closure.json` is explicitly classified as historical rather than current authority

Initial focused checkpoints were bounded to the three planned waves. A Wave 2 pytest launcher attempt stopped before collection because the description-tree conftest requires canonical full-gate seed bootstrap; no extra intermediate seed/full run was created. The same current VCS/import/package guard passed through its supported direct unittest route, and the CLI batch passed. Reviewer corrections ran only their affected CLI or G5 focused case immediately before the plan-required replacement terminal; no unrelated intermediate batch was added.

## Terminal results

- exact wheel: `C:/Users/MW/i/iris-build-validation-optimization-e0d22781/terminal/w7/wheel/iris_tooling-0.1.0-py3-none-any.whl`, SHA-256 `8063f8a20c1fc13fe5fb47f568ed80b1b086b272aafe38f764ddbe53d2483183`
- fresh environment receipt: `C:/Users/MW/i/iris-build-validation-optimization-e0d22781/terminal/w7/receipt/environment_receipt.json`, SHA-256 `b452af787e3afeabde15c689d508d55d9ba18e28cceb8e29428d286f9e442864`
- package timing: wheel build `0.938 s`, fresh environment/dependency/wheel provision `0.633 s`, one-shot environment writer `1.637 s`
- current launcher blobs at the machine subject: full gate `166a47d967ffc0838d8e734c2ffcf89162b87d99`; comparator `899a8d289f2669606f1123f2d4207947a6504610`
- Run A: exit `0`, `208.619 s`, orchestration `C:/Users/MW/i/ivo7-ra/orchestration.json`
- Run B: exit `0`, `208.381 s`, orchestration `C:/Users/MW/i/ivo7-rb/orchestration.json`
- Round3 current-route routing identity: `103 → 103`; this is routing membership, not the canonical full-gate pytest denominator
- both runs: `PASS`, canonical full-gate pytest identity `211 → 211` plus required standalone validation `4 → 4`, so recurring execution unit `211 + 4 = 215 → 215`; source checkout clean after, external execution status unchanged, external work root empty after
- canonical result SHA-256: A = B = `ef6072fdcc1e3dcb71b1cdfacae656bf9d9e7dfd0da027114dd4d18e3833a2ac`
- deterministic comparator: exit `0`, `2.629 s`, receipt `C:/Users/MW/i/ivo7-cmp/compare_receipt.json`, status `succeeded`, fingerprint `9e7bd8224a2ffe02ad49bfccd8950ec1e7f7715065b5bd303950127c125e3abc`
- final tracked mutation check before this documentation-only closeout edit: clean

Rerun discipline was fail-closed. Early launcher attempts stopped on the declared Windows path budget and a CRLF working-file versus LF Git-blob binding mismatch. Later independent review found three authority/CLI issues, then the missing `execution.py` and identity-owner closure constituents, and finally one cumulative-retention list replacement. Each implementation or test-contract correction produced the plan-required new package-source/environment subject and one exact terminal A/B/comparator bundle; no unchanged subject was rerun for extra confidence. Successors 0013 through 0016 were never rewritten, 0017 was added only for the real closure-set change, and the later retention-list correction did not create 0018. No reordered run, historical replay, or full tooling pytest was added.

The denominator excludes parameterized named cases, `subTest` constituent assertions, migration-only scripts, external census, Reviewer-only checks, and unregistered temporary validations. Both routing and canonical pytest identity deltas are zero; this work did not add 108 regular tests.

Independent Reviewer result: PASS — actionable finding `0`, unsupported claim `0`, unsupported retention `0`, unimplemented eligible optimization `0`, product/runtime/Lua mutation `0`. The final closure check was read-only and ran no additional tests.

## Physical lightweighting

These read-only Git object statistics compare product S0 `e6310737…` with final-including-Walkthrough `7f943745…`.

| Scope | S0 | Final including Walkthrough | Delta |
|---|---:|---:|---:|
| Iris files | 1,753 | 1,731 | -22 |
| Iris Git blob bytes | 71,766,663 | 70,970,753 | -795,910 |
| Whole-repository files | 6,935 | 6,917 | -18 |
| Whole-repository Git blob bytes | 142,715,144 | 142,003,274 | -711,870 |

The same range has `65 files changed, 3,259 insertions, 22,193 deletions`. These are physical Git blob/context surface reductions, not runtime performance, wall-clock performance, or token-efficiency measurements.

## Work timeline and execution churn

| Milestone | Commit timestamp (KST) |
|---|---|
| Plan carrier | 2026-08-27 11:11:34 |
| Main implementation | 2026-08-27 11:42:50 |
| Reviewed closeout | 2026-08-27 13:13:59 |
| Walkthrough carrier | 2026-08-27 13:24:01 |

The commit-timestamp intervals are about 31 minutes from plan to main implementation, 2 hours 2 minutes from plan to reviewed closeout, and 2 hours 12 minutes from plan to Walkthrough. They are outcome chronology only, not active compute time, exact Codex work time, or reconstructed pre-admission evidence.

The final terminal chain is `w7`. Six versioned environment authority records were added because each source/test/contract correction created a new exact package/environment subject; no unchanged subject was rerun merely for confidence. Static preflight could have caught the following avoidable churn earlier: composite CLI identity forwarding, the nested D16 reproduction glob, stale frozen Round3 closure, missing `execution.py` in G5, missing identity-owner self-inclusion, and 0016 replacement in cumulative required paths. This does not negate final correctness, Run A/B and comparator PASS, or Reviewer finding `0`, but the process is not claimed to have been perfectly efficient.

This documentation-only correction ran no tests, standalone validation, Run A/B, comparator, package build/install, writer, G5 validator, Lua syntax check, Reviewer, or historical replay.

> 이 closeout은 Iris build·validation execution 및 current-authority 탐색 최적화에만 귀속된다.  
> Wiki/Browser presentation 및 Lua UI 최적화의 완료를 주장하지 않는다.

또한 runtime performance/FPS, 실제 token 절감, release·Workshop·Publish·RTC readiness, 외부 모드 보편 compatibility와 stateful cross-run receipt ledger의 완성을 주장하지 않는다.
