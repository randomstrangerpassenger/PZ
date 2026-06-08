"""Quality Gate Q3 — Anchor role completeness."""
from quality.config import ALLOWED_EXEMPT_REASONS


def gate_q3(decisions: dict, candidates: dict, role_profiles: dict) -> dict:
    """
    PASS인 각 FullType의 rule_ids가 role profile을 충족하는지 검증.

    FAIL 조건:
    1. profile 미등록 rule_id가 PASS에 등장
    2. legacy=true인데 q3_exempt 필드 없음 (불완전 프로파일)
    3. q3_exempt=true인데 exempt_reason ∉ 허용 enum
    4. q3_exempt=true인데 legacy≠true (면제 남발 차단)
    5. required_roles 미충족 (non-exempt rules only)

    Evidence directionality: roles come from anchors only, never from prove.
    """
    violations = []
    checked = 0

    # ── Profile-level validation (한 번만 수행) ──
    for rid, profile in role_profiles.items():
        is_legacy = profile.get("legacy", False)
        q3_exempt = profile.get("q3_exempt")
        exempt_reason = profile.get("exempt_reason")

        # FAIL #2: legacy=true but q3_exempt missing
        if is_legacy and q3_exempt is None:
            violations.append(
                f"profile '{rid}': legacy=true but q3_exempt field missing"
            )

        # FAIL #4: q3_exempt=true but legacy!=true
        if q3_exempt is True and not is_legacy:
            violations.append(
                f"profile '{rid}': q3_exempt=true but legacy!=true"
            )

        # FAIL #3: q3_exempt=true but exempt_reason not in allowed enum
        if q3_exempt is True and exempt_reason not in ALLOWED_EXEMPT_REASONS:
            violations.append(
                f"profile '{rid}': exempt_reason='{exempt_reason}' "
                f"not in {sorted(ALLOWED_EXEMPT_REASONS)}"
            )

    # ── Per-item role validation ──
    for ft, dec in decisions.items():
        if dec["decision"] != "PASS":
            continue
        checked += 1

        rule_ids = dec.get("rule_ids", [])

        # ── Collect actual anchor roles (only from real anchor objects) ──
        actual_roles = set()
        cand = candidates.get(ft, {})
        for anchor in cand.get("anchors", []):
            role = anchor.get("role")
            if role:
                actual_roles.add(role)
        for anchor in dec.get("anchors", []):
            role = anchor.get("role")
            if role:
                actual_roles.add(role)

        for rid in rule_ids:
            # FAIL #1: unregistered rule
            if rid not in role_profiles:
                violations.append(
                    f"{ft}: rule_id '{rid}' not registered in "
                    f"role_profile_by_rule_id.json"
                )
                continue

            profile = role_profiles[rid]

            # Skip role check for exempt profiles
            if profile.get("q3_exempt") is True:
                continue

            required = set(profile.get("required_roles", []))
            missing = required - actual_roles

            if missing:
                violations.append(
                    f"{ft}: rule={rid} missing roles {sorted(missing)}"
                )

    status = "FAIL" if violations else "PASS"
    return {
        "status": status,
        "checked": checked,
        "violations": len(violations),
        "details": violations[:10] if violations else [],
    }
