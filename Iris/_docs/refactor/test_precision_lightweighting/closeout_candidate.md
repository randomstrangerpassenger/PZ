# Iris test precision lightweighting closeout candidate

State: `blocked_before_terminal_validation`

The implementation achieves the A1 reduction classifier on the fixed clean-checkout comparison domain: configured nodes `646 -> 645`, redundant scenarios `-1`, test-support LOC `27709 -> 27619`, files at least 500 LOC `10 -> 9`, files at least 1,000 LOC `2 -> 1`, and large test methods `22 -> 20`. Static precision comparison reports `precision_regression=0`; exact-current passes `219/219` with a clean post-run checkout.

The Change 8 Safety Exit Gate is not PASS. Configured-current ended with `458 passed, 1 skipped, 3 failed, 9 errors`, and the canonical historical route is blocked by the existing lower-conftest option bootstrap/mixed-item denominator behavior. The failures are preserved as failures and are not reclassified as a successful closeout.

No `S_terminal` was frozen. Consequently no terminal Run A/B attestation, Codex Reviewer terminal verdict, owner seal, bundle manifest, closeout receipt, or retrieval report was created. The pre-ratified external bundle allocation remains unused for terminal claims.
