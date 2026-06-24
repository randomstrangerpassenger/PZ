# Round 3 Scope Lock

Generated: `2026-06-11T12:14:22+00:00`

Authority order:

1. `docs/Philosophy.md`
2. `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
3. `docs/iris-round3-final-integrated-build-script-test-contract-disentanglement-plan.md`
4. `Iris/_docs/refactor/round3_tools_build_test_contract_roadmap.md`
5. `Iris/_docs/round3/*` evidence artifacts

Primary provenance paths are repo-stable. This round does not use attachment-only provenance.

Staging policy: no staging or commit is in scope for this execution turn. Primary evidence remains untracked until the owner stages or requests staging.

## Gate Records

```text
gate_id: D1
decision: approved
approved_by: user in current Codex chat
timestamp: 2026-06-11T21:18:56+09:00
allowed_scope: Change 4 unittest-compatible manifest runner route; no pytest routing; no test moves
blocked_scope: pytest routing; physical test moves; archive/delete/disposition
evidence_artifact: Iris/_docs/round3/round3_discovery_reconciliation.md
status: approved

gate_id: D2
decision: approved_limited_non_destructive
approved_by: user in current Codex chat
timestamp: 2026-06-11T21:30:09+09:00
allowed_scope: Change 5 disposition manifest/log/ledger only; keep/current/historical/diagnostic/manifest-only classification
blocked_scope: physical archive; delete; relocation; .gitignore edits; filename-glob cleanup
evidence_artifact: Iris/_docs/round3/round3_disposition_log.md
status: approved_limited

gate_id: D3
decision: approved
approved_by: user in current Codex chat
timestamp: 2026-06-11T21:30:09+09:00
allowed_scope: Change 6 closeout with historical preservation policy pass_required
blocked_scope: release readiness; runtime equivalence; full historical artifact reproducibility; archive/delete safety; pytest parity
evidence_artifact: Iris/_docs/round3/round3_d3_historical_preservation_policy.json
status: approved

gate_id: D4
decision: approved
approved_by: user in current Codex chat
timestamp: 2026-06-11T21:51:00+09:00
allowed_scope: pytest default route narrowing; automated package gate; archive/delete no-op execution report; historical artifact reproducibility audit
blocked_scope: destructive archive/delete without non-empty proof candidate set; runtime equivalence; in-game manual QA; Workshop publication readiness; false full-artifact byte reproducibility claim
evidence_artifact: Iris/_docs/round3/round3_pytest_route_report.md
status: approved
```

## Source Roadmap Lock Checks

| Check | Status |
| --- | --- |
| exists | True |
| has_phase_1_to_6_headings | True |
| has_no_phase_0_alias | True |
| phase7a_followup_not_current_execution | True |
| historical_380_not_live_canonical | True |

## Tool Preflight

| Command | Exit Code |
| --- | --- |
| python --version | 0 |
| rg --version | 0 |
| jq --version | 0 |
| git status --short | 0 |

## Claim Boundary

This scope lock records measurement, classification evidence, contract-route separation, pytest default-route narrowing, archive/delete no-op execution, non-destructive disposition, and automated package-gate readiness. It does not claim runtime equivalence, in-game manual QA, Workshop publication readiness, full historical artifact byte reproducibility, or universal deletion safety.
