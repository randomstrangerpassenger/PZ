# Round 3 Disposition Log

Generated: `2026-06-11T12:51:00+00:00`

## D2 Decision

```text
gate_id: D2
decision: approved_limited_non_destructive
approved_by: user in current Codex chat
timestamp: 2026-06-11T12:51:00+00:00
allowed_scope: Change 5 disposition manifest/log/ledger only; keep/current/historical/diagnostic/manifest-only classification
blocked_scope: physical archive; delete; relocation; .gitignore edits; filename-glob cleanup
evidence_artifact: Iris/_docs/round3/round3_disposition_log.md
status: approved_limited
```

## Summary

| Metric | Count |
|---|---:|
| disposition rows | 281 |
| retained non-current rows | 269 |
| archive eligible | 0 |
| delete eligible | 0 |
| archive/delete actions executed | 0 |

Owner classes:

| Owner Class | Count |
|---|---:|
| current_build_core | 12 |
| diagnostic_advisory | 95 |
| historical_reproduction | 173 |
| manifest_only_candidate | 1 |

Final dispositions:

| Final Disposition | Count |
|---|---:|
| keep_current_core | 12 |
| keep_diagnostic_advisory | 95 |
| keep_historical_reproduction | 173 |
| keep_manifest_only | 1 |

Manifest-only retained rows:

| Path | Reason |
|---|---|
| `Iris/build/description/v2/tools/build/validate_interaction_cluster_seed.py` | D2 limited approval: artifact-path-only candidate retained as manifest-only; not archive/delete eligible without separate proof. |

## Route Evidence

| Route | Count | Success | Report |
|---|---:|---|---|
| current | 44 | True | `Iris/_docs/round3/round3_current_test_run.json` |
| historical | 284 | True | `Iris/_docs/round3/round3_historical_test_run.json` |
| diagnostic | 79 | True | `Iris/_docs/round3/round3_diagnostic_test_run.json` |
| boundary guard | n/a | True | `Iris/_docs/round3/round3_boundary_guard_report.json` |

## Invariant Result

No row is archive/delete eligible under D2. Every current-closure,
historical, diagnostic, doc/path-reference, artifact-path, peer-import,
test-import, dynamic/path-execution, or unresolved signal is retained.

Actual file movement, archive output, delete, or `.gitignore` disposition edit
is intentionally absent from this round.
