# Phase 0 decision matrix

| Decision | Disposition | Basis |
|---|---|---|
| Runtime Generator | `selected`: mandatory facade dedup; full removal `deferred_by_design` | Frozen classifications do not enumerate the complete runtime item universe or every primary-subcategory input, so full PZ corpus parity cannot be sealed. |
| Clean-checkout helpers | `selected`: `partial_reuse` | Existing helper owns canonical bytes/hash, Git identity/blob reads, external-root validation, and disposable checkout lifecycle. The new validator owns only this refactor's manifest lifecycle and mode orchestration. |
| Staging disposition | `selected`: in-place role manifest; no deletion | Historical/reproduction consumers exist and no zero-consumer disposable staging set is proven. |
| Build common extraction | `deferred_by_design` | Current core is 12 and allowed tooling is 4/4 with zero remaining slots. No residual defect justifies a slot change in this execution. |
| `getGroupVariants` / `IrisData` | `selected`: compatibility adapter, retain signature | No internal caller was found, but the Phase 0 supported API boundary includes the public facade and unknown external consumers are not disproved. |
| Capability facade | `selected`: retain | Browser interaction code consumes `getCapabilities`/`hasCapability`. |
| Taxonomy | `selected`: presentation boundary only | CategoryIndex owns labels/order projection; classification authority stays in generated classification/rule data. |
| `.gitignore` | `selected`: exact additive rules only | New tests are ignored by the existing exact test-root rule. |
| Food unit mismatch | `selected`: preserve existing output during refactor | `renderFoodSection` and `renderCoreInfoSection` use different scaling. PZ evidence will describe it; any correction is a separate approved change. |
| Repository cleanup | `not_applicable` | No material path satisfies zero consumer, zero required reference, zero package reachability, and zero reproduction requirement. |

