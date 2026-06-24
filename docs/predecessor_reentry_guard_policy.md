# Predecessor Reentry Guard Policy

Status: `adopted_required_gate_governance_policy`.

Predecessor values `2105`, `2084`, and `21` are allowed only in historical predecessor trace, frozen comparison baseline, successor evidence contract denominator, migration provenance, or terminal disposition provenance contexts.

Forbidden contexts:

- current hard gate
- current runtime authority
- package authority
- release readiness
- current debt
- required migration target expansion
- old chunks, monolith, or legacy bridge fallback
- raw predecessor artifact direct execution authority read

This policy does not delete predecessor trace. It prevents predecessor trace from becoming current authority, runtime authority, current debt, package authority, or release readiness.
