"""Quality Gate Q2 — Strong integrity."""


def gate_q2(overlay: dict) -> dict:
    """Strong/Weak 분류와 matched_fulltypes 카운트 정합성 검증."""
    violations = []
    checked = 0
    by_rule = overlay.get("by_rule_id", {})

    for rid, entry in by_rule.items():
        uniqueness = entry.get("uniqueness")
        if uniqueness is None:
            continue  # NO-only rule, skip
        checked += 1
        pass_count = entry.get("pass_count", 0)

        if uniqueness == "STRONG" and pass_count != 1:
            violations.append(
                f"{rid}: STRONG but pass_count={pass_count} (expected 1)"
            )
        elif uniqueness == "WEAK" and pass_count == 1:
            violations.append(
                f"{rid}: WEAK but pass_count=1 (should be STRONG)"
            )

    status = "FAIL" if violations else "PASS"
    return {
        "status": status,
        "checked": checked,
        "violations": len(violations),
        "details": violations[:10] if violations else [],
    }
