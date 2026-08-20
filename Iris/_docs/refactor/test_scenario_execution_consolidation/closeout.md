# Iris test scenario execution consolidation closeout

Status: `implementation_complete_canonical_validation_pass`.

The combined validation subject is commit `ea94c19789fd33799180c4cbf1e19bde26a3a482`, tree `f1f98eb73de5c3458f0553427e1791fbd696346b`. It contains the four-group expansion rooted at `c29eba99f24be459d83cd189806754041dd2cc20` and the source-classification alignment applied after that expansion. The prior three-group subject was `991414badc7d470c04bad2967dd26e78aff0b697`.

The adopted source plan is `docs/iris_test_scenario_execution_consolidation_plan.md`, SHA-256 `2e56a9c7dbda4f44f972ff9aa265b8c64d655049db1c460230619381b857a36b`. The source plan was not copied into the branch; its exact hash is retained for reproducibility.

## Structural consolidation outcome

| Scenario group | Comparable consolidatable invocations | Reduction | Total invocations | Evidence category |
| --- | ---: | ---: | ---: | --- |
| `artifact-inventory-git-fixture-seed` | 14 -> 2 | 85.71% | 35 -> 26 | qualified proxy |
| `registry-authority-common-source-compile` | 16 -> 1 | 93.75% | 16 -> 1 | qualified proxy |
| `registry-authority-round3-runner-source-compile` | 3 -> 1 | 66.67% | 3 -> 1 | qualified proxy |
| `artifact-promotion-git-fixture-seed` | 40 -> 2 | 95.00% | 133 -> 98 | qualified proxy |

The four cost-adopted groups cover 40 unique consumer nodes. The identity map contains 55 concrete node/case rows. It has zero duplicate new checkpoint IDs, zero unmapped terminal dispositions, and no old-test-ID drift.

The aggregate structural disclosure is 73 -> 6 consolidatable invocations and 187 -> 126 disclosed total invocations. These figures combine heterogeneous Git-producer and source-compilation signatures. They are qualified structural proxies, not wall-time, removable-cost, or performance claims.

The runtime-payload workspace change remains an isolation-only correction: one import-time writable global root became one class-owned read-only root plus six case-owned writable roots. Its materialization count intentionally changed from 1 to 7 and has `cost_claim=none`.

## Identity and denominator preservation

- Consolidation identity: 55 -> 55.
- Exact-current nodes: 219 -> 219, zero drift.
- Configured-current nodes: 471 -> 471.
- Configured denominator: 645 -> 645.
- Configured deselected nodes: 174 -> 174.
- Required source inventory: 63 -> 63.
- Required dependency paths: 40 -> 40, with no added or removed path.
- Required path-set SHA-256: `679bfa997002187d6b1fbfc3301017d82ff9d0d9db6c50f96c86db04cff94f4a`.
- Gate canonical dependency SHA-256: `2598b902cf82a6eb0c5b21faa9799552b7df7683461d526467aa14682160290c`.

The baseline/final dependency comparison receipt is `C:/Users/MW/Downloads/coding/PZ_alignment_55_receipts/final3/dependency_inventory_comparison.json`, SHA-256 `99a4eb9c590da1273af1991129f9e5dafc25cf003675e682760227ff1ad5e175`.

## Canonical validation

The exact combined subject `ea94c19789fd33799180c4cbf1e19bde26a3a482` was validated twice from clean disposable checkouts.

- Run A: native exit code 0; 424 passed, 0 failed, 2 deselected, 102 subtests passed, and 4 standalone validations passed. Orchestration receipt: `C:/Users/MW/iaca/r55j/o.json`, SHA-256 `7e49ad346cef5207d202a322ad2c798e4e323ca7f06fb87622373691c7ae0d90`.
- Run B: native exit code 0; 424 passed, 0 failed, 2 deselected, 102 subtests passed, and 4 standalone validations passed. Orchestration receipt: `C:/Users/MW/iaca/r55k/o.json`, SHA-256 `5b43b4ef0024da4b931f31283a396cf4cb56b7533081d388bf0965744a236e43`.
- Both canonical result files have SHA-256 `77cd75046c01ac2fb83e316d8dcd9e68d93cb52b7e46285ce013cb091d308bcb`.
- The deterministic comparator succeeded with native exit code 0. Receipt: `C:/Users/MW/iaca/r55l/compare_receipt.json`, SHA-256 `1d50f3c93f41475daa0e649aa62571eada1e48ce372c7344f2324d421ddad187`.
- Canonical fingerprint SHA-256: `60c65f596fb21d791351d8082afb9c4c49eb304e8c26f91bb9c63439ad05fe16`.
- Final sealed-artifact blob mismatch count: 0.

The earlier `991414ba` execution that stopped before pytest on an unclassified source remains historical failure evidence only. It is superseded by the exact combined-subject Run A/B results and is not reused as PASS evidence.

## Review and evidence closeout

The append-only authority closeout is commit `c41464fe9ee67974a0ffb43579dea4d5a93b6527`, tree `182afc4a09c6b88073e23e0f5108c5edcecd53be`. Codex Reviewer Round 3 approved that authority state with P0/P1/P2/P3 `0/0/0/0` and ran no tests.

The final adoption receipt is `C:/Users/MW/Downloads/coding/PZ_alignment_55_receipts/adoption/final_adoption_receipt_0012.json`, SHA-256 `c69b69c057199a521d51f6b2718852a0f24fdaf9b66205fcf19ce8c196dcc65c`.

Accordingly, the four-group implementation, 55-identity preservation, source classification, isolation, denominator, required dependency inventory, sealed-artifact, canonical validation, deterministic equivalence, and authority closeout axes are complete. The configured and full-gate performance axes remain outside the claim: no wall-time or removable-cost conclusion is made.
