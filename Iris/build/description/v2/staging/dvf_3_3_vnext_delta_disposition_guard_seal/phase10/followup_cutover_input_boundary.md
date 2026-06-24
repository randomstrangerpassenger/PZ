# Follow-up Cutover Input Boundary

Later cutover rounds must gate on `cutover_input_usable == true`, not on terminal string prefix or closeout state alone.

Current boundary: manifest/index-only and blocked by rejected rows.

- Approved delta manifest: `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal/phase9/approved_cutover_input_delta_manifest.json`
- Rejected absence report: `Iris/build/description/v2/staging/dvf_3_3_vnext_delta_disposition_guard_seal/phase9/rejected_delta_absence_from_cutover_input_report.json`
- Runtime parity report: `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_report.json`
- Runtime parity deltas: `Iris/build/description/v2/staging/dvf_3_3_vnext_regeneration_parity/phase5/runtime_parity_deltas.jsonl`
