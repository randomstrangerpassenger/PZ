# Codebase Feasibility Findings

- Prior rejected state rows are all `adopted -> unadopted`.
- Source decision rows share `silent / MISSING_PRIMARY_USE / cluster_absent_keep_existing / role_fallback_too_hollow`.
- Existing parity runner reads the live partial input manifest, so this round uses a corrected staging-local source manifest.
- Existing disposition guard builder is prior blocked-round specific, so this round owns a corrected success disposition contract.
