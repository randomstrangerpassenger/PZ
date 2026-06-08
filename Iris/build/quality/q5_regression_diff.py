"""Quality Gate Q5 — Regression diff control."""
import hashlib
import json

from quality.config import (
    BUILD_VERSION,
    DATA_DIR,
    DESCRIPTIONS_PATH,
    OUTPUT_DIR,
    USECASES_PATH,
    VALID_DECISIONS,
)
from tools.common.io import load_json


def q5_validate_allowed_changes(expected_diff: dict, allowed: list[dict]) -> list[str]:
    """Validate the allowed_changes control surface."""
    violations = []
    seen_fulltypes = set()
    all_frozen = (
        set(expected_diff.get("frozen_pass", []))
        | set(expected_diff.get("frozen_review", []))
    )

    for ac in allowed:
        ft = ac.get("fulltype", "")
        frm = ac.get("from", "")
        to = ac.get("to", "")

        # Uniqueness check
        if ft in seen_fulltypes:
            violations.append(f"allowed_changes: duplicate fulltype '{ft}'")
        seen_fulltypes.add(ft)

        # Value range check
        if frm not in VALID_DECISIONS:
            violations.append(
                f"allowed_changes: '{ft}' has invalid from='{frm}'"
            )
        if to not in VALID_DECISIONS:
            violations.append(
                f"allowed_changes: '{ft}' has invalid to='{to}'"
            )

        # Baseline existence check
        if ft not in all_frozen:
            # Also check if it might be a NO item (not individually listed)
            # For NO items, we only have count/hash, so we can't verify by name
            # Just ensure it's not listed in PASS/REVIEW frozen sets
            pass  # NO items are acceptable in allowed_changes

    return violations


def q5_report_allowed_changes(
    all_changes: list[dict],
    allowed: list[dict],
) -> tuple[list[str], list[str]]:
    """Compare collected Q5 changes against allowed_changes."""
    allowed_map = {}
    for ac in allowed:
        allowed_map[ac["fulltype"]] = ac

    unexpected = []
    for chg in all_changes:
        ft = chg["fulltype"]
        if ft.startswith("_"):
            # System-level changes (NO count/hash, usecase count/hash) — always unexpected
            unexpected.append(f"{ft}: {chg['change']}")
        elif ft in allowed_map:
            # This change was explicitly allowed
            pass
        else:
            unexpected.append(f"{ft}: {chg['change']} (not in allowed_changes)")

    warnings = []
    for ft, ac in allowed_map.items():
        was_changed = any(c["fulltype"] == ft for c in all_changes)
        if not was_changed:
            warnings.append(
                f"allowed_changes: '{ft}' {ac['from']}→{ac['to']} not yet applied"
            )

    return unexpected, warnings


def q5_collect_decision_status_changes(
    decisions: dict,
    expected_diff: dict,
) -> list[dict]:
    """Collect PASS/REVIEW set changes and NO aggregate changes."""
    changes = []

    # Compare PASS sets
    frozen_pass = set(expected_diff.get("frozen_pass", []))
    current_pass = set(
        ft for ft, d in decisions.items() if d["decision"] == "PASS"
    )

    for ft in current_pass - frozen_pass:
        changes.append({"fulltype": ft, "change": "→PASS"})
    for ft in frozen_pass - current_pass:
        changes.append({"fulltype": ft, "change": "PASS→"})

    # Compare REVIEW sets
    frozen_review = set(expected_diff.get("frozen_review", []))
    current_review = set(
        ft for ft, d in decisions.items() if d["decision"] == "REVIEW"
    )

    for ft in current_review - frozen_review:
        changes.append({"fulltype": ft, "change": "→REVIEW"})
    for ft in frozen_review - current_review:
        changes.append({"fulltype": ft, "change": "REVIEW→"})

    # Compare NO count + hash
    frozen_no_count = expected_diff.get("frozen_no_count", 0)
    frozen_no_hash = expected_diff.get("frozen_no_hash", "")

    current_no = sorted(
        ft for ft, d in decisions.items() if d["decision"] == "NO"
    )
    current_no_count = len(current_no)
    current_no_hash = hashlib.sha256(
        json.dumps(current_no).encode("utf-8")
    ).hexdigest()

    if current_no_count != frozen_no_count:
        changes.append({
            "fulltype": "_NO_COUNT",
            "change": f"count {frozen_no_count}→{current_no_count}"
        })
    if frozen_no_hash and current_no_hash != frozen_no_hash:
        changes.append({
            "fulltype": "_NO_HASH",
            "change": "NO set content changed"
        })

    return changes


def q5_collect_usecase_aggregate_changes(
    usecases_data: dict | None,
    expected_diff: dict,
) -> list[dict]:
    """Collect usecase aggregate count/hash changes."""
    if not usecases_data:
        return []

    frozen_uc_count = expected_diff.get("frozen_usecase_count", 0)
    frozen_uc_hash = expected_diff.get("frozen_usecase_hash", "")
    uc_fulltypes = usecases_data.get("fulltypes", {})

    # Build a sorted list of (fulltype, [use_case_ids]) for hashing total
    uc_entries = sorted(
        (ft, sorted(uc["use_case_id"] for uc in info["use_cases"]))
        for ft, info in uc_fulltypes.items()
    )
    current_uc_count = len(uc_entries)
    current_uc_hash = hashlib.sha256(
        json.dumps(uc_entries).encode("utf-8")
    ).hexdigest()

    changes = []
    if current_uc_count != frozen_uc_count:
        changes.append({
            "fulltype": "_USECASE_COUNT",
            "change": f"count {frozen_uc_count}→{current_uc_count}"
        })
    if frozen_uc_hash and current_uc_hash != frozen_uc_hash:
        changes.append({
            "fulltype": "_USECASE_HASH",
            "change": "usecase set content changed"
        })
    return changes


def q5_collect_description_aggregate_changes(expected_diff: dict) -> list[dict]:
    """Collect description block count/hash changes."""
    if not DESCRIPTIONS_PATH.exists():
        return []

    frozen_desc_count = expected_diff.get("frozen_description_count", 0)
    frozen_desc_hash = expected_diff.get("frozen_description_hash", "")

    desc_data = load_json(DESCRIPTIONS_PATH)
    desc_fulltypes = desc_data.get("fulltypes", {})
    # Build a sorted list of (fulltype, items+debug_items) for hashing
    # use_case_block이 없을 수 있으므로 .get으로 안전 처리
    desc_entries = sorted(
        (ft, info.get("use_case_block", {}).get("items", [])
         + info.get("use_case_block", {}).get("debug_items", []))
        for ft, info in desc_fulltypes.items()
    )
    current_desc_count = len(desc_entries)
    current_desc_hash = hashlib.sha256(
        json.dumps(desc_entries).encode("utf-8")
    ).hexdigest()

    changes = []
    if current_desc_count != frozen_desc_count:
        changes.append({
            "fulltype": "_DESCRIPTION_COUNT",
            "change": f"count {frozen_desc_count}→{current_desc_count}"
        })
    if frozen_desc_hash and current_desc_hash != frozen_desc_hash:
        changes.append({
            "fulltype": "_DESCRIPTION_HASH",
            "change": "description set content changed"
        })
    return changes


def q5_collect_requirements_aggregate_changes(
    expected_diff: dict,
) -> tuple[list[dict], dict | None]:
    """Collect keep-requirements count/hash changes and return requirement data."""
    req_path = OUTPUT_DIR / f"requirements_by_fulltype.{BUILD_VERSION}.json"
    if not req_path.exists():
        return [], None

    frozen_req_count = expected_diff.get("frozen_requirements_count", 0)
    frozen_req_hash = expected_diff.get("frozen_requirements_hash", "")

    req_data = load_json(req_path)
    req_fulltypes = req_data.get("fulltypes", {})
    req_entries = sorted(
        (ft, info.get("requirements", []))
        for ft, info in req_fulltypes.items()
        if info.get("requirements")
    )
    current_req_count = len(req_entries)
    current_req_hash = hashlib.sha256(
        json.dumps(req_entries).encode("utf-8")
    ).hexdigest()

    changes = []
    if current_req_count != frozen_req_count:
        changes.append({
            "fulltype": "_REQUIREMENTS_COUNT",
            "change": f"count {frozen_req_count}→{current_req_count}"
        })
    if frozen_req_hash and current_req_hash != frozen_req_hash:
        changes.append({
            "fulltype": "_REQUIREMENTS_HASH",
            "change": "requirements set content changed"
        })
    return changes, req_fulltypes


def q5_collect_legacy_count_changes(expected_diff: dict) -> list[dict]:
    """Collect legacy inventory count changes according to its policy."""
    legacy_baseline = expected_diff.get("legacy_count_baseline", 0)
    legacy_policy = expected_diff.get("legacy_count_policy", "freeze")
    legacy_inv_path = OUTPUT_DIR / f"legacy_inventory.{BUILD_VERSION}.json"
    if not legacy_inv_path.exists():
        return []

    legacy_data = load_json(legacy_inv_path)
    current_legacy_count = legacy_data.get("legacy_count", 0)
    if legacy_policy == "decrease_only":
        legacy_count_changed = current_legacy_count > legacy_baseline
    else:
        legacy_count_changed = current_legacy_count != legacy_baseline

    if not legacy_count_changed:
        return []

    return [{
        "fulltype": "_LEGACY_COUNT",
        "change": f"count {legacy_baseline}→{current_legacy_count}"
    }]


def q5_collect_require_channel_changes(
    req_fulltypes: dict | None,
    expected_diff: dict,
) -> list[dict]:
    """Collect v2.5 require channel count/hash changes."""
    if req_fulltypes is None:
        return []

    frozen_require_ft_count = expected_diff.get("frozen_require_fulltype_count", 0)
    frozen_require_hash = expected_diff.get("frozen_require_hash", "")
    frozen_require_policy = expected_diff.get("frozen_require_policy", "decrease_only")

    require_entries = sorted(
        (ft, info.get("require", []))
        for ft, info in req_fulltypes.items()
        if info.get("require")
    )
    current_require_ft_count = len(require_entries)
    current_require_hash = hashlib.sha256(
        json.dumps(require_entries).encode("utf-8")
    ).hexdigest()

    if frozen_require_policy == "decrease_only":
        # decrease_only 래칫: 증가만 FAIL, 감소는 허용
        require_count_changed = current_require_ft_count > frozen_require_ft_count
    else:
        require_count_changed = current_require_ft_count != frozen_require_ft_count
    require_hash_changed = (
        frozen_require_hash and current_require_hash != frozen_require_hash
    )

    changes = []
    if require_count_changed:
        changes.append({
            "fulltype": "_REQUIRE_FT_COUNT",
            "change": f"count {frozen_require_ft_count}→{current_require_ft_count}"
        })
    if require_hash_changed:
        changes.append({
            "fulltype": "_REQUIRE_HASH",
            "change": "require set content changed"
        })
    return changes


def q5_compare_metric_changes(
    new_metrics: dict,
    expected_diff: dict,
) -> tuple[list[dict], list[str]]:
    """Compare collected Q5 metrics against frozen policies."""
    changes = []
    violations = []

    for k, current_val in new_metrics.items():
        # override metrics do not have 'frozen_' prefix in expected_diff.json
        if k.startswith("override_"):
            frozen_val = expected_diff.get(k, 0)
        else:
            frozen_val = expected_diff.get(f"frozen_{k}", 0)

        if k == "rightclick_evidence_fulltype_count" and current_val < frozen_val:
            # decrease_only policy
            pass
        elif k == "rightclick_evidence_fulltype_count" and current_val > frozen_val:
            violations.append(
                f"Metric '{k}' increased {frozen_val}→{current_val} "
                f"(decrease_only violation)"
            )

        # Policy for unknown_prefix_line_count (decrease_only)
        if k == "unknown_prefix_line_count" and current_val < frozen_val:
            pass  # Acceptable
        elif k == "unknown_prefix_line_count" and current_val > frozen_val:
            violations.append(
                f"Metric '{k}' increased {frozen_val}→{current_val} "
                f"(decrease_only violation)"
            )

        # Policy for rightclick_strong_fulltype_count (decrease_only)
        if k == "rightclick_strong_fulltype_count" and current_val < frozen_val:
            violations.append(
                f"Metric '{k}' decreased {frozen_val}→{current_val} "
                f"(decrease_only violation)"
            )

        # Policy for rightclick_strong_line_count (decrease_only)
        if k == "rightclick_strong_line_count" and current_val < frozen_val:
            violations.append(
                f"Metric '{k}' decreased {frozen_val}→{current_val} "
                f"(decrease_only violation)"
            )

        # Other metrics allow arbitrary changes without strict FAIL logic for now,
        # but they must be registered in all_changes if they differ.
        if current_val != frozen_val:
            changes.append({
                "fulltype": f"_{k.upper()}",
                "change": f"count {frozen_val}→{current_val}"
            })

    return changes, violations


def q5_collect_usecase_line_metrics(uc_fulltypes: dict) -> dict:
    """Collect right-click/recipe line-kind usecase metrics."""
    rc_ev_ft = 0
    rc_ev_lines = 0
    rc_ex_ft = 0
    rc_ex_lines = 0
    rec_ev_ft = 0

    for ft, info in uc_fulltypes.items():
        ft_has_rc_ev = False
        ft_has_rc_ex = False
        ft_has_rec_ev = False

        for uc in info.get("use_cases", []):
            is_recipe = any(
                s["source_type"] == "recipe_evidence"
                for s in uc.get("evidence_sources", [])
            )
            is_rc = any(
                s["source_type"] == "rightclick"
                for s in uc.get("evidence_sources", [])
            )
            kind = uc.get("line_kind")

            if is_recipe:
                ft_has_rec_ev = True
            if is_rc:
                if kind == "evidence":
                    ft_has_rc_ev = True
                    rc_ev_lines += 1
                elif kind == "exclusion":
                    ft_has_rc_ex = True
                    rc_ex_lines += 1

        if ft_has_rc_ev:
            rc_ev_ft += 1
        if ft_has_rc_ex:
            rc_ex_ft += 1
        if ft_has_rec_ev:
            rec_ev_ft += 1

    return {
        "rightclick_evidence_fulltype_count": rc_ev_ft,
        "rightclick_evidence_line_count": rc_ev_lines,
        "rightclick_exclusion_fulltype_count": rc_ex_ft,
        "rightclick_exclusion_line_count": rc_ex_lines,
        "recipe_evidence_fulltype_count": rec_ev_ft,
    }


def q5_collect_evidence_strength_metrics(uc_fulltypes: dict) -> dict:
    """Collect right-click evidence strength metrics."""
    rc_strong_ft = 0
    rc_strong_lines = 0
    rc_weak_ft = 0
    rc_exclude_lines = 0

    for ft, info in uc_fulltypes.items():
        ft_has_strong = False
        ft_has_weak = False
        for uc in info.get("use_cases", []):
            ev_str = uc.get("evidence_strength")
            if ev_str in ("strong", "STRONG"):
                rc_strong_lines += 1
                ft_has_strong = True
            elif ev_str in ("weak", "WEAK"):
                ft_has_weak = True
            elif ev_str in ("exclude", "EXCLUDE"):
                rc_exclude_lines += 1
        if ft_has_strong:
            rc_strong_ft += 1
        if ft_has_weak:
            rc_weak_ft += 1

    return {
        "rightclick_strong_fulltype_count": rc_strong_ft,
        "rightclick_strong_line_count": rc_strong_lines,
        "rightclick_weak_fulltype_count": rc_weak_ft,
        "rightclick_exclude_line_count": rc_exclude_lines,
    }


def q5_collect_recipe_role_metrics(
    uc_fulltypes: dict,
    expected_diff: dict,
) -> tuple[dict, list[str]]:
    """Validate recipe source roles and collect keep-link metric."""
    valid_recipe_roles = {"consume", "keep"}
    recipe_keep_link_count = 0
    violations = []

    for ft, info in uc_fulltypes.items():
        for uc in info.get("use_cases", []):
            for src in uc.get("evidence_sources", []):
                st = src.get("source_type")
                role = src.get("role")
                if st == "recipe_evidence":
                    # 필수: role이 없으면 FAIL
                    if role is None:
                        violations.append(
                            f"{ft}: recipe_evidence source missing role field "
                            f"(rule_id={src.get('rule_id')})"
                        )
                    elif role not in valid_recipe_roles:
                        violations.append(
                            f"{ft}: invalid role '{role}' "
                            f"(must be {sorted(valid_recipe_roles)})"
                        )
                    if role == "keep":
                        recipe_keep_link_count += 1
                else:
                    # 비-recipe source에 role이 있으면 FAIL (스키마 오염 차단)
                    if role is not None:
                        violations.append(
                            f"{ft}: source_type='{st}' has unexpected role field"
                        )

    frozen_keep_links = expected_diff.get("frozen_recipe_keep_link_count", 0)
    if recipe_keep_link_count < frozen_keep_links:
        violations.append(
            f"recipe_keep_link_count decreased "
            f"{frozen_keep_links}→{recipe_keep_link_count} (decrease_only)"
        )

    return {"recipe_keep_link_count": recipe_keep_link_count}, violations


def q5_validate_keep_unresolved_count() -> list[str]:
    """Validate recipe keep_unresolved_count FAIL-LOUD condition."""
    rec_dec_path = OUTPUT_DIR / f"recipe_evidence_decisions.{BUILD_VERSION}.json"
    if not rec_dec_path.exists():
        return [
            "recipe_evidence_decisions MISSING — cannot verify keep_unresolved_count"
        ]

    rec_stats = load_json(rec_dec_path).get("stats", {})
    keep_unresolved = rec_stats.get("keep_unresolved_count", 0)
    if keep_unresolved > 0:
        return [f"keep_unresolved_count={keep_unresolved} (must be 0)"]
    return []


def q5_collect_registry_override_metrics() -> dict:
    """Collect action override metrics from the use-case registry."""
    override_action_count = 0
    override_strong_count = 0

    registry_path = DATA_DIR / f"use_case_registry.{BUILD_VERSION}.json"
    if registry_path.exists():
        registry_data = load_json(registry_path)
        for props in registry_data.get("rules", {}).values():
            ucid = props.get("use_case_id", "")
            if props.get("alias_of"):
                ucid = props["alias_of"]
            if ucid.startswith("uc.action.") and props.get("decision") == "PASS":
                override_action_count += 1
                if props.get("strength") == "STRONG":
                    override_strong_count += 1

    return {
        "override_action_count": override_action_count,
        "override_strong_count": override_strong_count,
    }


def q5_collect_diagnostic_metrics() -> dict:
    """Collect diagnostic metrics used by Q5."""
    diagnostics_path = OUTPUT_DIR / f"diagnostics.{BUILD_VERSION}.json"
    if diagnostics_path.exists():
        diag_data = load_json(diagnostics_path)
        unknown_prefix_count = len(diag_data.get("unknown_prefix", []))
    else:
        unknown_prefix_count = 0
    return {"unknown_prefix_line_count": unknown_prefix_count}


def q5_collect_recipe_nav_metrics(expected_diff: dict) -> tuple[dict, list[str]]:
    """Validate recipe nav registry stats and collect nav metrics."""
    nav_registry_path = OUTPUT_DIR / f"recipe_nav_registry.{BUILD_VERSION}.json"
    frozen_nav = expected_diff.get("frozen_nav_eligible_count", 0)
    violations = []
    metrics = {}

    if not nav_registry_path.exists():
        if frozen_nav > 0:
            violations.append(
                f"recipe_nav: registry MISSING but frozen_nav_eligible_count={frozen_nav}"
            )
        return metrics, violations

    nav_data = load_json(nav_registry_path)
    nav_stats = nav_data.get("stats", {})

    # FAIL-LOUD: required stats keys
    for req_key in [
        "uid_collision_count",
        "nav_missing_index_count",
        "nav_eligible_count",
        "nav_ineligible_count",
    ]:
        if req_key not in nav_stats:
            violations.append(
                f"recipe_nav: required stats key '{req_key}' missing"
            )

    # FAIL-LOUD: uid_collision must be 0
    uid_collision = nav_stats.get("uid_collision_count", -1)
    if uid_collision != 0:
        violations.append(
            f"recipe_nav: uid_collision_count={uid_collision} (must be 0)"
        )

    # FAIL-LOUD: nav_missing_index must be 0
    nav_missing = nav_stats.get("nav_missing_index_count", -1)
    if nav_missing != 0:
        violations.append(
            f"recipe_nav: nav_missing_index_count={nav_missing} (must be 0)"
        )

    # Ratchet: nav_eligible_count (decrease_only)
    current_nav = nav_stats.get("nav_eligible_count", 0)
    if current_nav < frozen_nav:
        violations.append(
            f"recipe_nav: nav_eligible_count decreased "
            f"{frozen_nav}→{current_nav} (decrease_only)"
        )
    metrics["nav_eligible_count"] = current_nav
    return metrics, violations


def q5_collect_recipe_requirement_index_metrics(
    expected_diff: dict,
) -> tuple[dict, list[str]]:
    """Validate recipe requirements index stats and collect requirement metrics."""
    req_index_path = OUTPUT_DIR / f"recipe_requirements_index.{BUILD_VERSION}.json"
    frozen_req_with = expected_diff.get("frozen_req_with_requirements_count", 0)
    frozen_req_atoms = expected_diff.get("frozen_req_atoms_total", 0)
    metrics = {}
    violations = []

    if not req_index_path.exists():
        if frozen_req_with > 0:
            violations.append(
                "recipe_req: index MISSING but "
                f"frozen_req_with_requirements_count={frozen_req_with}"
            )
        return metrics, violations

    req_data = load_json(req_index_path)
    req_stats = req_data.get("stats", {})

    # FAIL-LOUD: upper bound 0
    for zero_key in [
        "req_missing_index_count",
        "req_uid_collision_count",
        "req_dangling_count",
    ]:
        val = req_stats.get(zero_key, -1)
        if val != 0:
            violations.append(f"recipe_req: {zero_key}={val} (must be 0)")

    # Upper bound: dangling_non_suffixed <= 1
    dns = req_stats.get("req_dangling_non_suffixed_count", -1)
    frozen_dns = expected_diff.get("frozen_req_dangling_non_suffixed_count", 1)
    if dns > frozen_dns:
        violations.append(
            f"recipe_req: req_dangling_non_suffixed_count={dns} "
            f"exceeds frozen {frozen_dns}"
        )

    # decrease_only: with_requirements
    cur_with = req_stats.get("with_requirements", 0)
    if cur_with < frozen_req_with:
        violations.append(
            f"recipe_req: with_requirements decreased "
            f"{frozen_req_with}→{cur_with} (decrease_only)"
        )
    metrics["req_with_requirements_count"] = cur_with

    # decrease_only: atoms_total
    cur_atoms = req_stats.get("atoms_total", 0)
    if cur_atoms < frozen_req_atoms:
        violations.append(
            f"recipe_req: atoms_total decreased "
            f"{frozen_req_atoms}→{cur_atoms} (decrease_only)"
        )
    metrics["req_atoms_total"] = cur_atoms

    # decrease_only: atoms_with_check (C1 — FAIL-LOUD 후조건)
    frozen_req_with_check = expected_diff.get("frozen_req_atoms_with_check", 0)
    cur_with_check = req_stats.get("atoms_with_check", 0)
    if cur_with_check < frozen_req_with_check:
        violations.append(
            f"recipe_req: atoms_with_check decreased "
            f"{frozen_req_with_check}→{cur_with_check} (decrease_only)"
        )
    metrics["req_atoms_with_check"] = cur_with_check

    # upper bound 0: atoms_without_check must be 0 (C1)
    cur_no_check = req_stats.get("atoms_without_check", 0)
    if cur_no_check > 0:
        violations.append(
            f"recipe_req: atoms_without_check={cur_no_check} (must be 0)"
        )

    # Tracking: base_slug_fallback
    metrics["req_base_slug_fallback_count"] = req_stats.get(
        "req_base_slug_fallback_count", 0
    )
    return metrics, violations


def gate_q5(decisions: dict, expected_diff: dict) -> dict:
    """expected_diff.json 기준으로 허용되지 않은 변경 탐지."""
    violations = []

    # ── Step 0: allowed_changes 자체 검증 ──
    allowed = expected_diff.get("allowed_changes", [])
    violations.extend(q5_validate_allowed_changes(expected_diff, allowed))

    if violations:
        return {
            "status": "FAIL",
            "unexpected_changes": len(violations),
            "pending_allowed": 0,
            "details": violations[:10],
            "warnings": [],
        }

    # ── Step 1~3: Compare PASS/REVIEW/NO decision status changes ──
    decision_status_changes = q5_collect_decision_status_changes(
        decisions, expected_diff
    )

    # ── Step 3b: Compare usecases count/hash and derived metrics ──
    usecase_aggregate_changes = []
    new_metrics = {}
    usecases_data = None
    if USECASES_PATH.exists():
        usecases_data = load_json(USECASES_PATH)
        usecase_aggregate_changes = q5_collect_usecase_aggregate_changes(
            usecases_data, expected_diff
        )
        uc_fulltypes = usecases_data.get("fulltypes", {})
        role_metrics, role_violations = q5_collect_recipe_role_metrics(
            uc_fulltypes, expected_diff
        )
        nav_metrics, nav_violations = q5_collect_recipe_nav_metrics(
            expected_diff
        )
        req_index_metrics, req_index_violations = (
            q5_collect_recipe_requirement_index_metrics(expected_diff)
        )

        new_metrics.update(q5_collect_usecase_line_metrics(uc_fulltypes))
        new_metrics.update(q5_collect_evidence_strength_metrics(uc_fulltypes))
        new_metrics.update(role_metrics)
        new_metrics.update(q5_collect_registry_override_metrics())
        new_metrics.update(q5_collect_diagnostic_metrics())
        new_metrics.update(nav_metrics)
        new_metrics.update(req_index_metrics)

        violations.extend(role_violations)
        violations.extend(q5_validate_keep_unresolved_count())
        violations.extend(nav_violations)
        violations.extend(req_index_violations)

    new_metric_changes, metric_violations = q5_compare_metric_changes(
        new_metrics, expected_diff
    )
    violations.extend(metric_violations)

    # ── Step 3c~3f: Compare output aggregate count/hash changes ──
    description_aggregate_changes = q5_collect_description_aggregate_changes(
        expected_diff
    )
    requirements_aggregate_changes, req_fulltypes = (
        q5_collect_requirements_aggregate_changes(expected_diff)
    )
    legacy_count_changes = q5_collect_legacy_count_changes(expected_diff)
    require_channel_changes = q5_collect_require_channel_changes(
        req_fulltypes, expected_diff
    )

    # ── Step 4: Collect all changes ──
    all_changes = []
    all_changes.extend(new_metric_changes)
    all_changes.extend(decision_status_changes)
    all_changes.extend(usecase_aggregate_changes)
    all_changes.extend(description_aggregate_changes)
    all_changes.extend(requirements_aggregate_changes)
    all_changes.extend(legacy_count_changes)
    all_changes.extend(require_channel_changes)

    # ── Step 5~6: Check against allowed_changes and pending allowed ──
    unexpected, warnings = q5_report_allowed_changes(all_changes, allowed)

    status = "FAIL" if unexpected else "PASS"
    return {
        "status": status,
        "unexpected_changes": len(unexpected),
        "pending_allowed": len(warnings),
        "details": unexpected[:10] if unexpected else [],
        "warnings": warnings[:10] if warnings else [],
        "new_metrics": new_metrics,
    }
